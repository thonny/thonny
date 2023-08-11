"""
Utils to handle different jedi versions
"""
import os.path
from logging import getLogger
from typing import Dict, List, Optional

import jedi.api.classes
from jedi.api.classes import BaseSignature, ParamName

from thonny.common import (
    CompletionInfo,
    NameReference,
    SignatureInfo,
    SignatureParameter,
    is_local_path,
)

logger = getLogger(__name__)

_last_jedi_completions: Optional[List[jedi.api.classes.Completion]] = None


def get_script_completions(
    source: str, row: int, column: int, filename: str, sys_path=None
) -> List[CompletionInfo]:
    global _last_jedi_completions
    try:
        script = _create_script(source, filename, sys_path)
        completions = script.complete(line=row, column=column, fuzzy=False)
    except Exception:
        logger.exception("Jedi error")
        completions = []

    completions = _filter_completions(completions, sys_path)
    _last_jedi_completions = completions
    return _export_completions(completions)


def get_interpreter_completions(
    source: str, namespaces: List[Dict], sys_path=None
) -> List[CompletionInfo]:
    global _last_jedi_completions
    try:
        interpreter = _create_interpreter(source, namespaces, sys_path)
        # assuming cursor is at the end of the source
        completions = interpreter.complete()
    except Exception:
        logger.exception("Jedi error")
        completions = []

    completions = _filter_completions(completions, sys_path)
    _last_jedi_completions = completions
    return _export_completions(completions)


def get_completion_details(full_name: str) -> Optional[CompletionInfo]:
    if not _last_jedi_completions:
        return None

    # assuming this name can be found in the list of last completions
    try:
        for completion in _last_jedi_completions:
            if completion.type in {"function", "class"}:
                signatures = [_export_signature(s) for s in completion.get_signatures()]
                raw_docstring = True
            else:
                signatures = None
                raw_docstring = False

            if completion.full_name == full_name:
                return CompletionInfo(
                    name=completion.name,
                    name_with_symbols=_get_completion_name_with_symbols(completion, signatures),
                    full_name=completion.full_name,
                    type=completion.type,
                    prefix_length=completion.get_completion_prefix_length(),
                    signatures=signatures,
                    docstring=completion.docstring(raw=raw_docstring),
                    module_name=completion.module_name,
                    module_path=completion.module_path and str(completion.module_path),
                )
    except Exception:
        logger.exception("Jedi error")

    return None


def get_script_signatures(
    source: str, row: int, column: int, filename: str, sys_path=None
) -> List[SignatureInfo]:
    try:
        script = _create_script(source, filename, sys_path)
        sigs = script.get_signatures(line=row, column=column)
    except Exception:
        sigs = []

    return [_export_signature(sig) for sig in sigs]


def get_interpreter_signatures(
    source: str, namespaces: List[Dict], sys_path=None
) -> List[SignatureInfo]:
    try:
        # assuming cursor is at the end of the source
        interpreter = _create_interpreter(source, namespaces, sys_path)
        sigs = interpreter.get_signatures()
    except Exception:
        logger.exception("Jedi error")
        sigs = []

    return [_export_signature(sig) for sig in sigs]


def get_definitions(
    source: str, row: int, column: int, filename: str, sys_path: List[str] = None
) -> List[NameReference]:
    try:
        script = _create_script(source, filename, sys_path)
        defs = script.goto(line=row, column=column, follow_imports=True)
    except Exception:
        logger.exception("Jedi error")
        defs = []

    return [_export_reference(d) for d in defs]


def get_references(
    source: str,
    row: int,
    column: int,
    filename: str,
    scope: str,
    sys_path: Optional[List[str]] = None,
) -> List[NameReference]:
    try:
        script = _create_script(source + ")", filename, sys_path)
        references = script.get_references(row, column, include_builtins=False, scope=scope)
    except Exception:
        logger.exception("Jedi error")
        return []

    # some refs (e.g. in Jedi 0.16) may lack line and column
    references = [ref for ref in references if ref.line is not None and ref.column is not None]

    return [_export_reference(ref) for ref in references]


def _create_script(source: str, filename: str, sys_path: List[str]) -> jedi.api.Script:
    # Beside local scripts, this is also used for MicroPython remote scripts and also in MP shell
    if filename and is_local_path(filename) or filename is None:
        # local and unnamed files
        project_path = os.getcwd()
        smart_sys_path = True
    else:
        # remote files and shell
        project_path = None
        smart_sys_path = False

    project = jedi.Project(path=project_path, sys_path=sys_path, smart_sys_path=smart_sys_path)

    return jedi.Script(
        code=source,
        path=filename,
        project=project,
    )


def _create_interpreter(
    source: str, namespaces: List[Dict], sys_path: Optional[List[str]]
) -> jedi.api.Interpreter:
    # not using this method for remote MicroPython, therefore it's OK to use cwd as project path
    project = jedi.Project(path=os.getcwd(), sys_path=sys_path)
    return jedi.Interpreter(source, namespaces, project=project)


def _export_completions(completions: List[jedi.api.classes.Completion]) -> List[CompletionInfo]:
    return [_export_completion(comp) for comp in completions]


def _filter_completions(
    completions: List[jedi.api.classes.Completion], sys_path: Optional[List[str]]
) -> List[jedi.api.classes.Completion]:
    if sys_path is None:
        return completions

    result = []
    for completion in completions:
        if completion.name.startswith("__"):
            continue

        result.append(completion)

    return result


def _export_completion(completion: jedi.api.classes.Completion) -> CompletionInfo:
    # In jedi before 0.16, the name attribute did not contain trailing '=' for argument completions,
    # since 0.16 it does.
    # When older jedi versions were supported, I needed to ensure similar result for all supported
    # versions.
    # Also, for MicroPython there are some completions which are not created by jedi.

    return CompletionInfo(
        name=completion.name and completion.name.strip("="),
        name_with_symbols=_get_completion_name_with_symbols(completion),
        full_name=completion.full_name and completion.full_name.strip("="),
        type=completion.type,
        prefix_length=completion.get_completion_prefix_length(),
        signatures=None,  # must be queried separately
        docstring=None,  # must be queried separately
        module_name=completion.module_name,
        module_path=completion.module_path and str(completion.module_path),
    )


def _export_signature(sig: BaseSignature) -> SignatureInfo:
    as_string = sig.to_string()
    if "->" in as_string:
        # No documented API for getting the return type in 0.18
        return_type = as_string.split("->")[-1].strip()
    else:
        return_type = None

    current_param_index = None
    call_bracket_start = None
    if hasattr(sig, "index"):
        # only in subclass (Signature or CallSignature)
        current_param_index = sig.index
    if hasattr(sig, "bracket_start"):
        # only in subclass (Signature or CallSignature)
        call_bracket_start = sig.bracket_start

    return SignatureInfo(
        name=sig.name,
        params=[_export_param(p) for p in sig.params],
        return_type=return_type,
        current_param_index=current_param_index,
        call_bracket_start=call_bracket_start,
    )


def _export_param(param: ParamName) -> SignatureParameter:
    # No documented API for getting separate annotation and default, need to parse
    s = param.to_string()

    if s.count("=") == 1:
        without_default, default = s.split("=")
    else:
        without_default = (s,)
        default = None

    if without_default.count(":") == 1:
        annotation = without_default.split(":")[-1].strip()
    else:
        annotation = None

    return SignatureParameter(
        kind=str(param.kind), name=param.name, annotation=annotation, default=default
    )


def _export_reference(ref) -> NameReference:
    return NameReference(
        module_name=ref.module_name,
        module_path=None if not ref.module_path else str(ref.module_path),
        row=ref.line,
        column=ref.column,
        length=len(ref.name),
    )


def _get_completion_name_with_symbols(
    completion: jedi.api.classes.Completion,
    signatures: Optional[List[BaseSignature]] = None,
) -> str:
    if completion.type == "param":
        # Older jedi versions may give trailing "=" also for actual arguments.
        # NB! Not all params are names of the params!
        return completion.name_with_symbols
    elif completion.type == "function":
        if not signatures:
            # signatures not found or haven't been computed yet
            return completion.name + "("
        else:
            # logger.info("name: %s, type: %s, sigs: %s", completion.name, completion.type, signatures)
            # assuming type=instance can also have signature
            # if it can only be called with 0 params, then add closing paren as well
            different_param_counts = {len(sig.params) for sig in signatures}
            if different_param_counts == {0}:
                return completion.name + "()"
            else:
                return completion.name + "("

    elif completion.type == "keyword" and completion.name != "pass":
        return completion.name + " "

    return completion.name_with_symbols
