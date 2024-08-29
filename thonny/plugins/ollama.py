from typing import Iterator, List

from thonny.assistance import Assistant, ChatContext, ChatMessage, ChatResponseChunk


class OllamaAssistant(Assistant):
    def get_ready(self) -> bool:
        return True

    def complete_chat(self, context: ChatContext) -> Iterator[ChatResponseChunk]:
        import ollama

        api_messages = [{"role": msg.role, "content": msg.content} for msg in context.messages]
        stream = ollama.chat(
            model="codellama:7b-instruct",
            messages=api_messages,
            stream=True,
        )

        for chunk in stream:
            yield ChatResponseChunk(chunk["message"]["content"], is_final=False)

        yield ChatResponseChunk("", is_final=True)

    def cancel_completion(self) -> None:
        pass
