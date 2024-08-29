import json
import random
import threading
import time
import uuid
from json import JSONDecodeError
from logging import getLogger
from tkinter import ttk
from typing import Any, Dict, Iterator, List, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from thonny import get_workbench
from thonny.assistance import Assistant, ChatContext, ChatMessage, ChatResponseChunk
from thonny.languages import tr
from thonny.misc_utils import get_and_parse_json, post_and_parse_json, post_and_return_stream
from thonny.ui_utils import create_url_label, show_dialog
from thonny.workdlg import WorkDialog

CLIENT_ID = "Iv1.b507a08c87ecfe98"

BASE_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "editor-version": "Neovim/0.9.2",
    "editor-plugin-version": "copilot.lua/1.11.4",
    "User-Agent": "GithubCopilot/1.133.0",
}

ACCESS_TOKEN_SECRET_KEY = "github_copilot_access_token"


logger = getLogger(__name__)


class GithubAccessTokenDialog(WorkDialog):
    def __init__(self, master):
        self.login_spec = None
        self.access_token = None
        super().__init__(master, autostart=True)

    def get_instructions(self) -> Optional[str]:
        return "Visit following URL to connect Thonny to your GitHub Copilot account:"

    def populate_main_frame(self):
        visit_label = ttk.Label(
            self.main_frame,
            text=f"Visit following URL to connect Thonny to your GitHub Copilot account:",
        )
        visit_label.grid(row=1, column=1, columnspan=2)

        self.url_label = None

        code_label = ttk.Label(self.main_frame, text="When asked, enter following code:")
        code_label.grid(row=3, column=1, columnspan=2)

        self.code_entry = ttk.Entry(self.main_frame, state="readonly")
        self.code_entry.grid(row=4, column=1)

        copy_button = ttk.Button(
            self.main_frame, text="Copy the code", command=self._copy_code_to_clipboard
        )
        copy_button.grid(row=4, column=2)

    def start_work(self):
        threading.Thread(target=self._work_in_thread).start()

    def _work_in_thread(self):
        self.login_spec = post_and_parse_json(
            "https://github.com/login/device/code",
            data={"client_id": CLIENT_ID, "scope": "read:user"},
            headers=BASE_HEADERS,
        )

        logger.info("Got following login spec: %r", self.login_spec)

        # Ui will soon pick up the change and present the URL and code. Start polling for the result.
        while True:
            time.sleep(self.login_spec["interval"])
            token = self.try_get_token_in_thread()
            if token is not None:
                self.access_token = token
                break

    def try_get_token_in_thread(self) -> Optional[str]:
        url = "https://github.com/login/oauth/access_token"

        response = post_and_parse_json(
            url,
            headers=BASE_HEADERS,
            data={
                "client_id": CLIENT_ID,
                "device_code": self.login_spec["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        )

        if "error" in response:
            logger.warning("Got error when querying access token: %r", response)
        else:
            # TODO: don't log private info!
            logger.debug("Got following response when querying access token: %r", response)

        return response.get("access_token", None)

    def _copy_code_to_clipboard(self):
        get_workbench().clipboard_clear()
        get_workbench().clipboard_append(self.code_entry.get())

    def update_ui(self):
        super().update_ui()
        if self.state == "closed":
            return

        if self.access_token is not None:
            self.report_done(True)
            return

        if self.login_spec is not None and self.code_entry.get() == "":
            self.code_entry.configure(state="normal")
            self.code_entry.insert(0, self.login_spec["user_code"])
            self.code_entry.configure(state="readonly")

            self.url_label = create_url_label(
                self.main_frame, url=self.login_spec["verification_uri"]
            )
            self.url_label.grid(row=2, column=1, columnspan=2)
            # TODO: show something about login_spec["expires_in"] ?


class GitHubCopilotAssistant(Assistant):
    def cancel_completion(self) -> None:
        # TODO:
        pass

    # Inspired by:
    # https://github.com/B00TK1D/copilot-api/blob/main/api.py
    # https://github.com/CopilotC-Nvim/CopilotChat.nvim/blob/b05861d034aaf89a481e8442107ecf97e896f13d/rplugin/python3/CopilotChat/copilot.py
    # https://github.com/zed-industries/zed/pull/14842

    def __init__(self):
        self.machine_id = "".join([random.choice("0123456789abcdef") for _ in range(65)])
        self._session_id: Optional[str] = None
        self._session_token: Optional[str] = None

    def get_ready(self) -> bool:
        if self._get_saved_access_token() is not None:
            return True

        self._request_new_access_token()
        return self._get_saved_access_token() is not None

    def _request_new_access_token(self):
        logger.info("Starting to request the access token")
        dlg = GithubAccessTokenDialog(get_workbench())
        show_dialog(dlg, get_workbench())
        self._save_access_token(dlg.access_token)
        # TODO: sensitive?
        logger.info("Got access token: %r", dlg.access_token)

    def _request_new_session_token(self):
        assert self._get_saved_access_token() is not None
        self._session_id = str(uuid.uuid4()) + str(round(time.time() * 1000))

        result = get_and_parse_json(
            "https://api.github.com/copilot_internal/v2/token",
            headers=BASE_HEADERS
            | {
                "authorization": f"token {self._get_saved_access_token()}",
            },
        )

        self._session_token = result.get("token", None)
        if self._session_token is None:
            raise RuntimeError(f"Could not get session token. API result: {result}")

    def _prepare_for_api_call(self):
        if not self._session_token_is_valid():
            self._request_new_session_token()

    def _session_token_is_valid(self) -> bool:
        if self._session_token is None:
            return False

        pairs = self._session_token.split(";")
        for pair in pairs:
            key, value = pair.split("=")
            if key.strip() == "exp":
                exp_time = int(value.strip())
                return exp_time > time.time()

        # Did not find "exp", let's be optimistic
        return True

    def _get_saved_access_token(self) -> Optional[str]:
        return get_workbench().get_secret(ACCESS_TOKEN_SECRET_KEY, None)

    def _save_access_token(self, value: Optional[str]):
        get_workbench().set_secret(ACCESS_TOKEN_SECRET_KEY, value)

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        self._prepare_for_api_call()

        api_messages = [{"role": msg.role, "content": msg.content} for msg in context.messages]
        body = {
            "intent": True,
            "model": "gpt-4",
            "n": 1,
            "stream": True,
            "temperature": 0.1,
            "top_p": 1,
            "messages": api_messages,
        }
        try:
            stream = post_and_return_stream(
                "https://api.githubcopilot.com/chat/completions",
                data=body,
                headers=self._get_api_headers(),
            )
        except HTTPError as e:
            messages_by_code = {
                401: "Unauthorized. Make sure you have access to Copilot Chat.",
                500: "Internal server error. Try again later.",
                400: "Your prompt has been rejected by Copilot Chat.",
                419: "You have been rate limited. Try again later.",
            }
            response_body = e.read()
            logger.error("complete_chat got error %r with body %r", e.code, response_body)
            user_message = messages_by_code.get(e.code, None)
            if user_message is None:
                user_message = f"Copilot returned error code {e.code} with following response:\n{response_body}"
            raise CopilotError(user_message) from e

        line_prefix = "data: "
        for line_bytes in stream:
            logger.info("Processing %r", line_bytes)
            if not line_bytes.strip():
                continue

            line = line_bytes.decode("utf-8")
            assert line.startswith(line_prefix)
            line_content = line[len(line_prefix) :].strip()
            if line_content == "[DONE]":
                break

            try:
                fragment = json.loads(line_content)
            except JSONDecodeError:
                logger.exception("Could not decode %r", line_content)
                raise

            choices = fragment["choices"]
            if len(choices) == 0:
                continue
            delta_content = choices[0]["delta"]["content"]
            if delta_content is None:
                continue

            yield ChatResponseChunk(delta_content, False)

        yield ChatResponseChunk("", True)

    def _get_api_headers(self) -> Dict[str, Any]:
        return {
            "authorization": f"Bearer {self._session_token}",
            "x-request-id": str(uuid.uuid4()),
            "vscode-sessionid": self._session_id,
            "machineid": self.machine_id,
            "editor-version": "vscode/1.85.1",
            "editor-plugin-version": "copilot-chat/0.12.2023120701",
            "openai-organization": "github-copilot",
            "openai-intent": "conversation-panel",
            "content-type": "application/json",
            "user-agent": "GitHubCopilotChat/0.12.2023120701",
        }


class CopilotError(RuntimeError):
    pass
