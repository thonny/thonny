import random
import threading
import time
import uuid
from logging import getLogger
from math import floor
from tkinter import ttk
from typing import Iterator, List, Optional

import grpc
from exa.chat_pb.chat_pb2 import ChatMessage, ChatMessageIntent, IntentGeneric
from exa.codeium_common_pb.codeium_common_pb2 import ChatMessageSource, Metadata
from exa.language_server_pb.language_server_pb2 import GetChatMessageRequest, GetChatMessageResponse
from exa.language_server_pb.language_server_pb2_grpc import LanguageServerServiceStub
from google.protobuf import timestamp_pb2

from thonny import get_workbench
from thonny.assistance import Assistant, ChatContext, ChatMessage, ChatResponseChunk
from thonny.misc_utils import post_and_parse_json
from thonny.ui_utils import create_url_label, show_dialog
from thonny.workdlg import WorkDialog

API_KEY_SECRET_KEY = "codeium_api_key"

logger = getLogger(__name__)


class CodeiumApiKeyDialog(WorkDialog):

    def __init__(self, master):
        self.api_key = None
        super().__init__(master)

    def get_title(self):
        return "Codeium API key"

    def get_instructions(self) -> Optional[str]:
        return (
            "1. Go to Codeium using the link provided below\n"
            "2. Log-in (if not already logged in)\n"
            "3. Copy your authorization key\n"
            "4. Paste it here\n"
            "5. Click OK"
        )

    def populate_main_frame(self):
        login_uuid = str(uuid.uuid4())
        url_label = create_url_label(
            self.main_frame,
            text="Click here to request Codeium authorization key (ignore the VSCode talk)...",
            url=f"https://www.codeium.com/profile?response_type=token&redirect_uri=show-auth-token&state={login_uuid}&scope=openid%20profile%20email&redirect_parameters_type=query",
        )
        url_label.grid(row=1, column=1, columnspan=2)

        self.key_entry = ttk.Entry(self.main_frame, width=50)
        self.key_entry.grid(row=2, column=1)

        paste_button = ttk.Button(self.main_frame, text="Paste the key", command=self._paste)
        paste_button.grid(row=1, column=2)

    def _paste(self):
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, get_workbench().clipboard_get())

    def start_work(self):
        threading.Thread(target=self._work_in_thread).start()

    def _work_in_thread(self):
        auth_token = self.key_entry.get()
        key_response = post_and_parse_json(
            "https://api.codeium.com/register_user/",
            data={"firebase_id_token": auth_token},
            headers={"Content-Type": "application/json"},
        )

        logger.info("Got following key response: %r", key_response)

        self.api_key = key_response["api_key"]

        self.report_done(True)


class CodeiumAssistant(Assistant):
    def __init__(self):
        self._ls_proc = None
        self._ls_port = None
        self._last_request_id = 0
        self._session_id: Optional[str] = None
        self._conversation_id = self._create_nonce()
        self._channel: Optional[grpc.Channel] = None
        self._ls_stub: Optional[LanguageServerServiceStub] = None

    def get_ready(self) -> bool:
        if self._ls_proc is None:
            self._start_language_server()

        if self._get_saved_api_key() is None:
            self._request_new_api_key()

        return self._ls_proc is not None and self._get_saved_api_key() is not None

    def _start_language_server(self):
        self._ls_proc = 1  # TODO: implement

    def _prepare_for_ls_call(self):
        # TODO: wait for LS ready state, if required (e.g. wait for port file or certain output)
        pass
        self._ls_port = 42100

        self._channel = grpc.insecure_channel(f"127.0.0.1:{self._ls_port}")
        self._ls_stub = LanguageServerServiceStub(self._channel)

    def _request_new_api_key(self):
        dlg = CodeiumApiKeyDialog(get_workbench())
        show_dialog(dlg, get_workbench())
        get_workbench().set_secret(API_KEY_SECRET_KEY, dlg.api_key)

    def _get_saved_api_key(self):
        return get_workbench().get_secret(API_KEY_SECRET_KEY, None)

    def _create_request_metadata(self):
        self._last_request_id += 1
        return Metadata(
            api_key=self._get_saved_api_key(),
            ide_name="jetbrains",
            ide_version="PyCharm 2023.1.1",
            extension_version="1.10.11",
            request_id=self._last_request_id,
            locale="en_US",
            session_id=self._session_id,
        )

    def _create_nonce(self) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return "".join([random.choice(alphabet) for _ in range(32)])

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        self._prepare_for_ls_call()

        proto_msgs = []

        for message in context.messages:

            if message.role == "user":
                source = ChatMessageSource.CHAT_MESSAGE_SOURCE_USER
            else:
                source = ChatMessageSource.CHAT_MESSAGE_SOURCE_SYSTEM

            proto_msg = ChatMessage(
                message_id=f"user-{uuid.uuid4()}",
                source=source,
                timestamp=timestamp_pb2.Timestamp(seconds=floor(time.time())),
                conversation_id=self._conversation_id,
                intent=ChatMessageIntent(generic=IntentGeneric(text=message.content)),
            )

            proto_msgs.append(proto_msg)

        response_stream = self._ls_stub.GetChatMessage(
            GetChatMessageRequest(
                metadata=self._create_request_metadata(),
                prompt="I want to learn programming",
                chat_messages=proto_msgs,
            )
        )

        last_prefix = ""
        for response in response_stream:
            assert isinstance(response, GetChatMessageResponse)
            resp_msg = response.chat_message
            if resp_msg.action and resp_msg.action.generic:
                text = resp_msg.action.generic.text
                assert text.startswith(last_prefix)
                yield ChatResponseChunk(text[len(last_prefix) :], False)
                last_prefix = text
            else:
                logger.info("Got unexpected ChatMessage: %s", resp_msg)

        yield ChatResponseChunk("", True)

    def cancel_completion(self) -> None:
        pass
