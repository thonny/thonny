# Adapted from https://github.com/predragnikolic/OLSP/

import json
import subprocess
from dataclasses import dataclass
from logging import getLogger
from queue import Queue
from typing import Any, Callable, Dict, List, Optional, Union

from thonny import get_workbench, lsp_types
from thonny.lsp_types import ErrorCodes, LspResponse, ResponseError

JSON_RPC_LEN_HEADER_PREFIX = b"Content-Length: "
JSON_RPC_TYPE_HEADER_PREFIX = b"Content-Type: "

logger = getLogger(__name__)


@dataclass
class CompletionParams:
    pass


METHOD_PARAMS_AND_RESPONSES = {"textDocument/completion": (CompletionParams,)}


class ResponseException(RuntimeError):
    def __init__(self, message: str, code: int = ErrorCodes.UnknownErrorCode, data: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def get_error(self) -> ResponseError:
        return ResponseError(message=self.message, code=self.code, data=self.data)


class JsonRpcError(RuntimeError):
    pass


class LanguageServerProxy:
    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._last_request_id: int = 0
        self._pending_callbacks: Dict[int, Callable] = {}
        self._request_handlers: Dict[str, Callable] = {}
        self._notification_handlers: Dict[str, List[Callable]] = {}
        self._unprocessed_messages_from_server: Queue[Dict] = Queue()

    def request_implementation(
        self,
        params: lsp_types.ImplementationParams,
        callback: Callable[
            [LspResponse[Union[lsp_types.Definition, List[lsp_types.LocationLink], None]]], None
        ],
    ) -> None:
        """A request to resolve the implementation locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such."""
        return self._send_request("textDocument/implementation", params, callback)

    def request_type_definition(
        self,
        params: lsp_types.TypeDefinitionParams,
        callback: Callable[
            [LspResponse[Union[lsp_types.Definition, List[lsp_types.LocationLink], None]]], None
        ],
    ) -> None:
        """A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such."""
        return self._send_request("textDocument/typeDefinition", params, callback)

    def request_document_color(
        self,
        params: lsp_types.DocumentColorParams,
        callback: Callable[[LspResponse[List[lsp_types.ColorInformation]]], None],
    ) -> None:
        """A request to list all color symbols found in a given text document. The request's
        parameter is of type {@link DocumentColorParams} the
        response is of type {@link ColorInformation ColorInformation[]} or a Thenable
        that resolves to such."""
        return self._send_request("textDocument/documentColor", params, callback)

    def request_color_presentation(
        self,
        params: lsp_types.ColorPresentationParams,
        callback: Callable[[LspResponse[List[lsp_types.ColorPresentation]]], None],
    ) -> None:
        """A request to list all presentation for a color. The request's
        parameter is of type {@link ColorPresentationParams} the
        response is of type {@link ColorInformation ColorInformation[]} or a Thenable
        that resolves to such."""
        return self._send_request("textDocument/colorPresentation", params, callback)

    def request_folding_range(
        self,
        params: lsp_types.FoldingRangeParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.FoldingRange], None]]], None],
    ) -> None:
        """A request to provide folding ranges in a document. The request's
        parameter is of type {@link FoldingRangeParams}, the
        response is of type {@link FoldingRangeList} or a Thenable
        that resolves to such."""
        return self._send_request("textDocument/foldingRange", params, callback)

    def request_declaration(
        self,
        params: lsp_types.DeclarationParams,
        callback: Callable[
            [LspResponse[Union[lsp_types.Declaration, List[lsp_types.LocationLink], None]]], None
        ],
    ) -> None:
        """A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Declaration}
        or a typed array of {@link DeclarationLink} or a Thenable that resolves
        to such."""
        return self._send_request("textDocument/declaration", params, callback)

    def request_selection_range(
        self,
        params: lsp_types.SelectionRangeParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.SelectionRange], None]]], None],
    ) -> None:
        """A request to provide selection ranges in a document. The request's
        parameter is of type {@link SelectionRangeParams}, the
        response is of type {@link SelectionRange SelectionRange[]} or a Thenable
        that resolves to such."""
        return self._send_request("textDocument/selectionRange", params, callback)

    def request_prepare_call_hierarchy(
        self,
        params: lsp_types.CallHierarchyPrepareParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.CallHierarchyItem], None]]], None],
    ) -> None:
        """A request to result a `CallHierarchyItem` in a document at a given position.
        Can be used as an input to an incoming or outgoing call hierarchy.

        @since 3.16.0"""
        return self._send_request("textDocument/prepareCallHierarchy", params, callback)

    def request_incoming_calls(
        self,
        params: lsp_types.CallHierarchyIncomingCallsParams,
        callback: Callable[
            [LspResponse[Union[List[lsp_types.CallHierarchyIncomingCall], None]]], None
        ],
    ) -> None:
        """A request to resolve the incoming calls for a given `CallHierarchyItem`.

        @since 3.16.0"""
        return self._send_request("callHierarchy/incomingCalls", params, callback)

    def request_outgoing_calls(
        self,
        params: lsp_types.CallHierarchyOutgoingCallsParams,
        callback: Callable[
            [LspResponse[Union[List[lsp_types.CallHierarchyOutgoingCall], None]]], None
        ],
    ) -> None:
        """A request to resolve the outgoing calls for a given `CallHierarchyItem`.

        @since 3.16.0"""
        return self._send_request("callHierarchy/outgoingCalls", params, callback)

    def request_semantic_tokens_full(
        self,
        params: lsp_types.SemanticTokensParams,
        callback: Callable[[LspResponse[Union[lsp_types.SemanticTokens, None]]], None],
    ) -> None:
        """@since 3.16.0"""
        return self._send_request("textDocument/semanticTokens/full", params, callback)

    def request_semantic_tokens_delta(
        self,
        params: lsp_types.SemanticTokensDeltaParams,
        callback: Callable[
            [LspResponse[Union[lsp_types.SemanticTokens, lsp_types.SemanticTokensDelta, None]]],
            None,
        ],
    ) -> None:
        """@since 3.16.0"""
        return self._send_request("textDocument/semanticTokens/full/delta", params, callback)

    def request_semantic_tokens_range(
        self,
        params: lsp_types.SemanticTokensRangeParams,
        callback: Callable[[LspResponse[Union[lsp_types.SemanticTokens, None]]], None],
    ) -> None:
        """@since 3.16.0"""
        return self._send_request("textDocument/semanticTokens/range", params, callback)

    def request_linked_editing_range(
        self,
        params: lsp_types.LinkedEditingRangeParams,
        callback: Callable[[LspResponse[Union[lsp_types.LinkedEditingRanges, None]]], None],
    ) -> None:
        """A request to provide ranges that can be edited together.

        @since 3.16.0"""
        return self._send_request("textDocument/linkedEditingRange", params, callback)

    def request_will_create_files(
        self,
        params: lsp_types.CreateFilesParams,
        callback: Callable[[LspResponse[Union[lsp_types.WorkspaceEdit, None]]], None],
    ) -> None:
        """The will create files request is sent from the client to the server before files are actually
        created as long as the creation is triggered from within the client.

        @since 3.16.0"""
        return self._send_request("workspace/willCreateFiles", params, callback)

    def request_will_rename_files(
        self,
        params: lsp_types.RenameFilesParams,
        callback: Callable[[LspResponse[Union[lsp_types.WorkspaceEdit, None]]], None],
    ) -> None:
        """The will rename files request is sent from the client to the server before files are actually
        renamed as long as the rename is triggered from within the client.

        @since 3.16.0"""
        return self._send_request("workspace/willRenameFiles", params, callback)

    def request_will_delete_files(
        self,
        params: lsp_types.DeleteFilesParams,
        callback: Callable[[LspResponse[Union[lsp_types.WorkspaceEdit, None]]], None],
    ) -> None:
        """The did delete files notification is sent from the client to the server when
        files were deleted from within the client.

        @since 3.16.0"""
        return self._send_request("workspace/willDeleteFiles", params, callback)

    def request_moniker(
        self,
        params: lsp_types.MonikerParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.Moniker], None]]], None],
    ) -> None:
        """A request to get the moniker of a symbol at a given text document position.
        The request parameter is of type {@link TextDocumentPositionParams}.
        The response is of type {@link Moniker Moniker[]} or `null`."""
        return self._send_request("textDocument/moniker", params, callback)

    def request_prepare_type_hierarchy(
        self,
        params: lsp_types.TypeHierarchyPrepareParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TypeHierarchyItem], None]]], None],
    ) -> None:
        """A request to result a `TypeHierarchyItem` in a document at a given position.
        Can be used as an input to a subtypes or supertypes type hierarchy.

        @since 3.17.0"""
        return self._send_request("textDocument/prepareTypeHierarchy", params, callback)

    def request_type_hierarchy_supertypes(
        self,
        params: lsp_types.TypeHierarchySupertypesParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TypeHierarchyItem], None]]], None],
    ) -> None:
        """A request to resolve the supertypes for a given `TypeHierarchyItem`.

        @since 3.17.0"""
        return self._send_request("typeHierarchy/supertypes", params, callback)

    def request_type_hierarchy_subtypes(
        self,
        params: lsp_types.TypeHierarchySubtypesParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TypeHierarchyItem], None]]], None],
    ) -> None:
        """A request to resolve the subtypes for a given `TypeHierarchyItem`.

        @since 3.17.0"""
        return self._send_request("typeHierarchy/subtypes", params, callback)

    def request_inline_value(
        self,
        params: lsp_types.InlineValueParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.InlineValue], None]]], None],
    ) -> None:
        """A request to provide inline values in a document. The request's parameter is of
        type {@link InlineValueParams}, the response is of type
        {@link InlineValue InlineValue[]} or a Thenable that resolves to such.

        @since 3.17.0"""
        return self._send_request("textDocument/inlineValue", params, callback)

    def request_inlay_hint(
        self,
        params: lsp_types.InlayHintParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.InlayHint], None]]], None],
    ) -> None:
        """A request to provide inlay hints in a document. The request's parameter is of
        type {@link InlayHintsParams}, the response is of type
        {@link InlayHint InlayHint[]} or a Thenable that resolves to such.

        @since 3.17.0"""
        return self._send_request("textDocument/inlayHint", params, callback)

    def request_resolve_inlay_hint(
        self,
        params: lsp_types.InlayHint,
        callback: Callable[[LspResponse[lsp_types.InlayHint]], None],
    ) -> None:
        """A request to resolve additional properties for an inlay hint.
        The request's parameter is of type {@link InlayHint}, the response is
        of type {@link InlayHint} or a Thenable that resolves to such.

        @since 3.17.0"""
        return self._send_request("inlayHint/resolve", params, callback)

    def request_text_document_diagnostic(
        self,
        params: lsp_types.DocumentDiagnosticParams,
        callback: Callable[[LspResponse[lsp_types.DocumentDiagnosticReport]], None],
    ) -> None:
        """The document diagnostic request definition.

        @since 3.17.0"""
        return self._send_request("textDocument/diagnostic", params, callback)

    def request_workspace_diagnostic(
        self,
        params: lsp_types.WorkspaceDiagnosticParams,
        callback: Callable[[LspResponse[lsp_types.WorkspaceDiagnosticReport]], None],
    ) -> None:
        """The workspace diagnostic request definition.

        @since 3.17.0"""
        return self._send_request("workspace/diagnostic", params, callback)

    def request_initialize(
        self,
        params: lsp_types.InitializeParams,
        callback: Callable[[LspResponse[lsp_types.InitializeResult]], None],
    ) -> None:
        """The initialize request is sent from the client to the server.
        It is sent once as the request after starting up the server.
        The requests parameter is of type {@link InitializeParams}
        the response if of type {@link InitializeResult} of a Thenable that
        resolves to such."""
        return self._send_request("initialize", params, callback)

    def request_shutdown(self, callback: Callable[[LspResponse[None]], None]) -> None:
        """A shutdown request is sent from the client to the server.
        It is sent once when the client decides to shutdown the
        server. The only notification that is sent after a shutdown request
        is the exit event."""
        return self._send_request("shutdown", None, callback)

    def request_will_save_wait_until(
        self,
        params: lsp_types.WillSaveTextDocumentParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TextEdit], None]]], None],
    ) -> None:
        """A document will save request is sent from the client to the server before
        the document is actually saved. The request can return an array of TextEdits
        which will be applied to the text document before it is saved. Please note that
        clients might drop results if computing the text edits took too long or if a
        server constantly fails on this request. This is done to keep the save fast and
        reliable."""
        return self._send_request("textDocument/willSaveWaitUntil", params, callback)

    def request_completion(
        self,
        params: lsp_types.CompletionParams,
        callback: Callable[
            [LspResponse[Union[List[lsp_types.CompletionItem], lsp_types.CompletionList, None]]],
            None,
        ],
    ) -> None:
        """Request to request completion at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response
        is of type {@link CompletionItem CompletionItem[]} or {@link CompletionList}
        or a Thenable that resolves to such.

        The request can delay the computation of the {@link CompletionItem.detail `detail`}
        and {@link CompletionItem.documentation `documentation`} properties to the `completionItem/resolve`
        request. However, properties that are needed for the initial sorting and filtering, like `sortText`,
        `filterText`, `insertText`, and `textEdit`, must not be changed during resolve."""
        return self._send_request("textDocument/completion", params, callback)

    def request_resolve_completion_item(
        self,
        params: lsp_types.CompletionItem,
        callback: Callable[[LspResponse[lsp_types.CompletionItem]], None],
    ) -> None:
        """Request to resolve additional information for a given completion item.The request's
        parameter is of type {@link CompletionItem} the response
        is of type {@link CompletionItem} or a Thenable that resolves to such."""
        return self._send_request("completionItem/resolve", params, callback)

    def request_hover(
        self,
        params: lsp_types.HoverParams,
        callback: Callable[[LspResponse[Union[lsp_types.Hover, None]]], None],
    ) -> None:
        """Request to request hover information at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response is of
        type {@link Hover} or a Thenable that resolves to such."""
        return self._send_request("textDocument/hover", params, callback)

    def request_signature_help(
        self,
        params: lsp_types.SignatureHelpParams,
        callback: Callable[[LspResponse[Union[lsp_types.SignatureHelp, None]]], None],
    ) -> None:
        return self._send_request("textDocument/signatureHelp", params, callback)

    def request_definition(
        self,
        params: lsp_types.DefinitionParams,
        callback: Callable[
            [LspResponse[Union[lsp_types.Definition, List[lsp_types.LocationLink], None]]], None
        ],
    ) -> None:
        """A request to resolve the definition location of a symbol at a given text
        document position. The request's parameter is of type [TextDocumentPosition]
        (#TextDocumentPosition) the response is of either type {@link Definition}
        or a typed array of {@link DefinitionLink} or a Thenable that resolves
        to such."""
        return self._send_request("textDocument/definition", params, callback)

    def request_references(
        self,
        params: lsp_types.ReferenceParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.Location], None]]], None],
    ) -> None:
        """A request to resolve project-wide references for the symbol denoted
        by the given text document position. The request's parameter is of
        type {@link ReferenceParams} the response is of type
        {@link Location Location[]} or a Thenable that resolves to such."""
        return self._send_request("textDocument/references", params, callback)

    def request_document_highlight(
        self,
        params: lsp_types.DocumentHighlightParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.DocumentHighlight], None]]], None],
    ) -> None:
        """Request to resolve a {@link DocumentHighlight} for a given
        text document position. The request's parameter is of type [TextDocumentPosition]
        (#TextDocumentPosition) the request response is of type [DocumentHighlight[]]
        (#DocumentHighlight) or a Thenable that resolves to such."""
        return self._send_request("textDocument/documentHighlight", params, callback)

    def request_document_symbol(
        self,
        params: lsp_types.DocumentSymbolParams,
        callback: Callable[
            [
                LspResponse[
                    Union[List[lsp_types.SymbolInformation], List[lsp_types.DocumentSymbol], None]
                ]
            ],
            None,
        ],
    ) -> None:
        """A request to list all symbols found in a given text document. The request's
        parameter is of type {@link TextDocumentIdentifier} the
        response is of type {@link SymbolInformation SymbolInformation[]} or a Thenable
        that resolves to such."""
        return self._send_request("textDocument/documentSymbol", params, callback)

    def request_code_action(
        self,
        params: lsp_types.CodeActionParams,
        callback: Callable[
            [LspResponse[Union[List[Union[lsp_types.Command, lsp_types.CodeAction]], None]]], None
        ],
    ) -> None:
        """A request to provide commands for the given text document and range."""
        return self._send_request("textDocument/codeAction", params, callback)

    def request_resolve_code_action(
        self,
        params: lsp_types.CodeAction,
        callback: Callable[[LspResponse[lsp_types.CodeAction]], None],
    ) -> None:
        """Request to resolve additional information for a given code action.The request's
        parameter is of type {@link CodeAction} the response
        is of type {@link CodeAction} or a Thenable that resolves to such."""
        return self._send_request("codeAction/resolve", params, callback)

    def request_workspace_symbol(
        self,
        params: lsp_types.WorkspaceSymbolParams,
        callback: Callable[
            [
                LspResponse[
                    Union[List[lsp_types.SymbolInformation], List[lsp_types.WorkspaceSymbol], None]
                ]
            ],
            None,
        ],
    ) -> None:
        """A request to list project-wide symbols matching the query string given
        by the {@link WorkspaceSymbolParams}. The response is
        of type {@link SymbolInformation SymbolInformation[]} or a Thenable that
        resolves to such.

        @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
         need to advertise support for WorkspaceSymbols via the client capability
         `workspace.symbol.resolveSupport`.
        """
        return self._send_request("workspace/symbol", params, callback)

    def request_resolve_workspace_symbol(
        self,
        params: lsp_types.WorkspaceSymbol,
        callback: Callable[[LspResponse[lsp_types.WorkspaceSymbol]], None],
    ) -> None:
        """A request to resolve the range inside the workspace
        symbol's location.

        @since 3.17.0"""
        return self._send_request("workspaceSymbol/resolve", params, callback)

    def request_code_lens(
        self,
        params: lsp_types.CodeLensParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.CodeLens], None]]], None],
    ) -> None:
        """A request to provide code lens for the given text document."""
        return self._send_request("textDocument/codeLens", params, callback)

    def request_resolve_code_lens(
        self,
        params: lsp_types.CodeLens,
        callback: Callable[[LspResponse[lsp_types.CodeLens]], None],
    ) -> None:
        """A request to resolve a command for a given code lens."""
        return self._send_request("codeLens/resolve", params, callback)

    def request_document_link(
        self,
        params: lsp_types.DocumentLinkParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.DocumentLink], None]]], None],
    ) -> None:
        """A request to provide document links"""
        return self._send_request("textDocument/documentLink", params, callback)

    def request_resolve_document_link(
        self,
        params: lsp_types.DocumentLink,
        callback: Callable[[LspResponse[lsp_types.DocumentLink]], None],
    ) -> None:
        """Request to resolve additional information for a given document link. The request's
        parameter is of type {@link DocumentLink} the response
        is of type {@link DocumentLink} or a Thenable that resolves to such."""
        return self._send_request("documentLink/resolve", params, callback)

    def request_formatting(
        self,
        params: lsp_types.DocumentFormattingParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TextEdit], None]]], None],
    ) -> None:
        """A request to to format a whole document."""
        return self._send_request("textDocument/formatting", params, callback)

    def request_range_formatting(
        self,
        params: lsp_types.DocumentRangeFormattingParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TextEdit], None]]], None],
    ) -> None:
        """A request to to format a range in a document."""
        return self._send_request("textDocument/rangeFormatting", params, callback)

    def request_on_type_formatting(
        self,
        params: lsp_types.DocumentOnTypeFormattingParams,
        callback: Callable[[LspResponse[Union[List[lsp_types.TextEdit], None]]], None],
    ) -> None:
        """A request to format a document on type."""
        return self._send_request("textDocument/onTypeFormatting", params, callback)

    def request_rename(
        self,
        params: lsp_types.RenameParams,
        callback: Callable[[LspResponse[Union[lsp_types.WorkspaceEdit, None]]], None],
    ) -> None:
        """A request to rename a symbol."""
        return self._send_request("textDocument/rename", params, callback)

    def request_prepare_rename(
        self,
        params: lsp_types.PrepareRenameParams,
        callback: Callable[[LspResponse[Union[lsp_types.PrepareRenameResult, None]]], None],
    ) -> None:
        """A request to test and perform the setup necessary for a rename.

        @since 3.16 - support for default behavior"""
        return self._send_request("textDocument/prepareRename", params, callback)

    def request_execute_command(
        self,
        params: lsp_types.ExecuteCommandParams,
        callback: Callable[[LspResponse[Union[lsp_types.LSPAny, None]]], None],
    ) -> None:
        """A request send from the client to the server to execute a command. The request might return
        a workspace edit which the client will apply to the workspace."""
        return self._send_request("workspace/executeCommand", params, callback)

    def notify_did_change_workspace_folders(
        self, params: lsp_types.DidChangeWorkspaceFoldersParams
    ) -> None:
        """The `workspace/didChangeWorkspaceFolders` notification is sent from the client to the server when the workspace
        folder configuration changes."""
        return self._send_notification("workspace/didChangeWorkspaceFolders", params)

    def notify_cancel_work_done_progress(
        self, params: lsp_types.WorkDoneProgressCancelParams
    ) -> None:
        """The `window/workDoneProgress/cancel` notification is sent from  the client to the server to cancel a progress
        initiated on the server side."""
        return self._send_notification("window/workDoneProgress/cancel", params)

    def notify_did_create_files(self, params: lsp_types.CreateFilesParams) -> None:
        """The did create files notification is sent from the client to the server when
        files were created from within the client.

        @since 3.16.0"""
        return self._send_notification("workspace/didCreateFiles", params)

    def notify_did_rename_files(self, params: lsp_types.RenameFilesParams) -> None:
        """The did rename files notification is sent from the client to the server when
        files were renamed from within the client.

        @since 3.16.0"""
        return self._send_notification("workspace/didRenameFiles", params)

    def notify_did_delete_files(self, params: lsp_types.DeleteFilesParams) -> None:
        """The will delete files request is sent from the client to the server before files are actually
        deleted as long as the deletion is triggered from within the client.

        @since 3.16.0"""
        return self._send_notification("workspace/didDeleteFiles", params)

    def notify_did_open_notebook_document(
        self, params: lsp_types.DidOpenNotebookDocumentParams
    ) -> None:
        """A notification sent when a notebook opens.

        @since 3.17.0"""
        return self._send_notification("notebookDocument/didOpen", params)

    def notify_did_change_notebook_document(
        self, params: lsp_types.DidChangeNotebookDocumentParams
    ) -> None:
        return self._send_notification("notebookDocument/didChange", params)

    def notify_did_save_notebook_document(
        self, params: lsp_types.DidSaveNotebookDocumentParams
    ) -> None:
        """A notification sent when a notebook document is saved.

        @since 3.17.0"""
        return self._send_notification("notebookDocument/didSave", params)

    def notify_did_close_notebook_document(
        self, params: lsp_types.DidCloseNotebookDocumentParams
    ) -> None:
        """A notification sent when a notebook closes.

        @since 3.17.0"""
        return self._send_notification("notebookDocument/didClose", params)

    def notify_initialized(self, params: lsp_types.InitializedParams) -> None:
        """The initialized notification is sent from the client to the
        server after the client is fully initialized and the server
        is allowed to send requests from the server to the client."""
        return self._send_notification("initialized", params)

    def notify_exit(self) -> None:
        """The exit event is sent from the client to the server to
        ask the server to exit its process."""
        return self._send_notification("exit", None)

    def notify_workspace_did_change_configuration(
        self, params: lsp_types.DidChangeConfigurationParams
    ) -> None:
        """The configuration change notification is sent from the client to the server
        when the client's configuration has changed. The notification contains
        the changed configuration as defined by the language client."""
        return self._send_notification("workspace/didChangeConfiguration", params)

    def notify_did_open_text_document(self, params: lsp_types.DidOpenTextDocumentParams) -> None:
        """The document open notification is sent from the client to the server to signal
        newly opened text documents. The document's truth is now managed by the client
        and the server must not try to read the document's truth using the document's
        uri. Open in this sense means it is managed by the client. It doesn't necessarily
        mean that its content is presented in an editor. An open notification must not
        be sent more than once without a corresponding close notification send before.
        This means open and close notification must be balanced and the max open count
        is one."""
        return self._send_notification("textDocument/didOpen", params)

    def notify_did_change_text_document(
        self, params: lsp_types.DidChangeTextDocumentParams
    ) -> None:
        """The document change notification is sent from the client to the server to signal
        changes to a text document."""
        return self._send_notification("textDocument/didChange", params)

    def notify_did_close_text_document(self, params: lsp_types.DidCloseTextDocumentParams) -> None:
        """The document close notification is sent from the client to the server when
        the document got closed in the client. The document's truth now exists where
        the document's uri points to (e.g. if the document's uri is a file uri the
        truth now exists on disk). As with the open notification the close notification
        is about managing the document's content. Receiving a close notification
        doesn't mean that the document was open in an editor before. A close
        notification requires a previous open notification to be sent."""
        return self._send_notification("textDocument/didClose", params)

    def notify_did_save_text_document(self, params: lsp_types.DidSaveTextDocumentParams) -> None:
        """The document save notification is sent from the client to the server when
        the document got saved in the client."""
        return self._send_notification("textDocument/didSave", params)

    def notify_will_save_text_document(self, params: lsp_types.WillSaveTextDocumentParams) -> None:
        """A document will save notification is sent from the client to the server before
        the document is actually saved."""
        return self._send_notification("textDocument/willSave", params)

    def notify_did_change_watched_files(
        self, params: lsp_types.DidChangeWatchedFilesParams
    ) -> None:
        """The watched files notification is sent from the client to the server when
        the client detects changes to file watched by the language client."""
        return self._send_notification("workspace/didChangeWatchedFiles", params)

    def notify_set_trace(self, params: lsp_types.SetTraceParams) -> None:
        return self._send_notification("$/setTrace", params)

    def notify_cancel_request(self, params: lsp_types.CancelParams) -> None:
        return self._send_notification("$/cancelRequest", params)

    def notify_progress(self, params: lsp_types.ProgressParams) -> None:
        return self._send_notification("$/progress", params)

    def bind_workspace_folders(
        self, callback: Callable[[None], Union[None, List[lsp_types.WorkspaceFolder]]]
    ):
        """The `workspace/workspaceFolders` is sent from the server to the client to fetch the open workspace folders."""
        self._bind_request_handler("workspace/workspaceFolders", callback)

    def bind_configuration(
        self, callback: Callable[[lsp_types.ConfigurationParams], List[lsp_types.LSPAny]]
    ):
        """The 'workspace/configuration' request is sent from the server to the client to fetch a certain
        configuration setting.

        This pull model replaces the old push model where the client signaled configuration change via an
        event. If the server still needs to react to configuration changes (since the server caches the
        result of `workspace/configuration` requests) the server should register for an empty configuration
        change event and empty the cache if such an event is received."""
        self._bind_request_handler("workspace/configuration", callback)

    def bind_work_done_progress_create(
        self, callback: Callable[[lsp_types.WorkDoneProgressCreateParams], None]
    ):
        """The `window/workDoneProgress/create` request is sent from the server to the client to initiate progress
        reporting from the server."""
        self._bind_request_handler("window/workDoneProgress/create", callback)

    def bind_semantic_tokens_refresh(self, callback: Callable[[None], None]):
        self._bind_request_handler("workspace/semanticTokens/refresh", callback)

    def bind_show_document(
        self, callback: Callable[[lsp_types.ShowDocumentParams], lsp_types.ShowDocumentResult]
    ):
        """A request to show a document. This request might open an
        external program depending on the value of the URI to open.
        For example a request to open `https://code.visualstudio.com/`
        will very likely open the URI in a WEB browser.

        @since 3.16.0"""
        self._bind_request_handler("window/showDocument", callback)

    def bind_show_message_request(
        self,
        callback: Callable[
            [lsp_types.ShowMessageRequestParams], Union[lsp_types.MessageActionItem, None]
        ],
    ):
        """The show message request is sent from the server to the client to show a message
        and a set of options actions to the user."""
        self._bind_request_handler("window/showMessageRequest", callback)

    def bind_inline_value_refresh(self, callback: Callable[[None], None]):
        self._bind_request_handler("workspace/inlineValue/refresh", callback)

    def bind_inline_hint_refresh(self, callback: Callable[[None], None]):
        self._bind_request_handler("workspace/inlineHint/refresh", callback)

    def bind_diagnostic_refresh(self, callback: Callable[[None], None]):
        """The diagnostic refresh request definition.

        @since 3.17.0"""
        self._bind_request_handler("workspace/diagnostic/refresh", callback)

    def bind_code_lens_refresh(self, callback: Callable[[None], None]):
        """A request to refresh all code actions

        @since 3.16.0"""
        self._bind_request_handler("workspace/codeLens/refresh", callback)

    def bind_register_capability(self, callback: Callable[[lsp_types.RegistrationParams], None]):
        """The `client/registerCapability` request is sent from the server to the client to register a new capability
        handler on the client side."""
        self._bind_request_handler("client/registerCapability", callback)

    def bind_unregister_capability(
        self, callback: Callable[[lsp_types.UnregistrationParams], None]
    ):
        """The `client/unregisterCapability` request is sent from the server to the client to unregister a previously
        registered capability handler on the client side."""
        self._bind_request_handler("client/unregisterCapability", callback)

    def bind_apply_edit(
        self,
        callback: Callable[
            [lsp_types.ApplyWorkspaceEditParams], lsp_types.ApplyWorkspaceEditResult
        ],
    ):
        """A request sent from the server to the client to modified certain resources."""
        self._bind_request_handler("workspace/applyEdit", callback)

    def bind_show_message(self, callback: Callable[[lsp_types.ShowMessageParams], None]):
        """The show message notification is sent from a server to a client to ask
        the client to display a particular message in the user interface."""
        self._bind_notification_handler("window/showMessage", callback)

    def bind_log_message(self, callback: Callable[[lsp_types.LogMessageParams], None]):
        """The log message notification is sent from the server to the client to ask
        the client to log a particular message."""
        self._bind_notification_handler("window/logMessage", callback)

    def bind_telemetry_event(self, callback: Callable[[lsp_types.LSPAny], None]):
        """The telemetry event notification is sent from the server to the client to ask
        the client to log telemetry data."""
        self._bind_notification_handler("telemetry/event", callback)

    def bind_publish_diagnostics(
        self, callback: Callable[[lsp_types.PublishDiagnosticsParams], None]
    ):
        """Diagnostics notification are sent from the server to the client to signal
        results of validation runs."""
        self._bind_notification_handler("textDocument/publishDiagnostics", callback)

    def bind_log_trace(self, callback: Callable[[lsp_types.LogTraceParams], None]):
        self._bind_notification_handler("$/logTrace", callback)

    def _bind_notification_handler(self, method: str, handler: Callable[[Any], None]) -> None:
        if method not in self._notification_handlers:
            self._notification_handlers[method] = []

        self._notification_handlers[method].append(handler)

    def _bind_request_handler(self, method: str, handler: Callable[[Any], Any]) -> None:
        if method in self._request_handlers:
            raise RuntimeError(f"Handler for {method!r} is already set")

        self._request_handlers[method] = handler

    def _process_messages_from_server(self) -> None:
        while not self._unprocessed_messages_from_server.empty():
            msg = self._unprocessed_messages_from_server.get()
            try:
                self._handle_message_from_server(msg)
            except Exception:
                # TODO: make it less invasive?
                get_workbench().report_exception()

    def _send_request(
        self, method: str, params: Any, callback: Callable[[LspResponse[Any]], None]
    ) -> None:
        request_id = self._last_request_id + 1
        self._last_request_id = request_id
        self._pending_callbacks[request_id] = callback
        self._send_json_rpc_message(
            {"jsonrpc": "2.0", "method": method, "id": request_id, "params": params}
        )

    def _send_notification(self, method: str, params: Any) -> None:
        self._send_json_rpc_message({"jsonrpc": "2.0", "method": method, "params": params})

    def _send_response(
        self, request_id: Union[str, int], result: Any, error: Optional[ResponseError] = None
    ) -> None:
        self._send_json_rpc_message(
            {"jsonrpc": "2.0", "id": request_id, "result": result, "error": error}
        )

    def _send_json_rpc_message(self, msg: Dict) -> None:
        json_bytes = json.dumps(msg).encode("utf-8")
        self._proc.stdin.write(JSON_RPC_LEN_HEADER_PREFIX)
        self._proc.stdin.write(str(len(json_bytes)).encode("utf-8"))
        self._proc.stdin.write(b"\r\n\r\n")
        self._proc.stdin.write(json_bytes)
        self._proc.stdin.flush()

    def _server_process_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _listen_stdout(self) -> None:
        """Runs in a background thread"""
        while self._server_process_alive():
            msg = _read_json_rpc_message(self._proc)
            self._unprocessed_messages_from_server.put(msg)

    def _handle_message_from_server(self, msg: Dict) -> None:
        method = msg.get("method")
        result = msg.get("result")
        error = msg.get("error")
        request_id = msg.get("id")
        params = msg.get("params")

        if method is not None:
            if request_id is not None:
                self._handle_request_from_server(request_id, method, params)
            else:
                self._handle_notification_from_server(method, params)
        elif request_id is not None:
            self._handle_response_from_server(request_id, result, error)
        else:
            raise RuntimeError(f"Don't know how to handle {msg}")

    def _handle_response_from_server(self, request_id, result, error):
        if request_id in self._pending_callbacks:
            callback = self._pending_callbacks[request_id]
            del self._pending_callbacks[request_id]
            callback(LspResponse(result, error))
        else:
            logger.info("Ignoring response for request %r", request_id)

    def _handle_request_from_server(
        self, request_id: Union[int, str], method: str, params: Any
    ) -> None:
        if method not in self._request_handlers:
            self._send_response(
                request_id=request_id,
                result=None,
                error=ResponseError(
                    message=f"No handler for {method}", code=ErrorCodes.MethodNotFound
                ),
            )
            raise RuntimeError(f"Handler for {method!r} is not set")

        try:
            result = self._request_handlers[method](params)
            self._send_response(request_id=request_id, result=result)
        except Exception as e:
            logger.exception("Handling %r failed", method)
            if isinstance(e, ResponseException):
                error = e.get_error()
            else:
                error = ResponseError(message=str(e), code=ErrorCodes.InternalError)
            self._send_response(request_id=request_id, result=None, error=error)

    def _handle_notification_from_server(self, method: str, params: Any) -> None:
        for handler in self._notification_handlers.get(method, []):
            handler(params)


def _read_json_rpc_message(proc: subprocess.Popen) -> Optional[Dict]:
    message_size = None
    while True:
        line: bytes = proc.stdout.readline()
        if not line:
            logger.info("Language server EOF")
            return

        if not line.endswith(b"\r\n"):
            raise JsonRpcError("Header without newline")

        # remove the "\r\n"
        line = line[:-2]

        if line == b"":
            # separator of headers and content
            break
        elif line.startswith(JSON_RPC_LEN_HEADER_PREFIX):
            line = line[len(JSON_RPC_LEN_HEADER_PREFIX) :]
            if not line.isdigit():
                raise JsonRpcError("Bad header: size is not int")
            message_size = int(line)
        elif line.startswith(JSON_RPC_TYPE_HEADER_PREFIX):
            pass
        else:
            raise JsonRpcError(f"Unknown header {line!r}")

        if not message_size:
            raise JsonRpcError("Bad header: missing size")

        jsonrpc_res = proc.stdout.read(message_size)
        return json.loads(jsonrpc_res)
