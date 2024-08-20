from typing import Iterator, List

from thonny.assistance import AiChatMessage, AiChatResponseFragment, AiProvider


class OllamaAiProvider(AiProvider):
    def get_ready(self) -> bool:
        return True

    def complete_chat(self, messages: List[AiChatMessage]) -> Iterator[AiChatResponseFragment]:
        import ollama

        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        stream = ollama.chat(
            model="codellama:7b-instruct",
            messages=api_messages,
            stream=True,
        )

        for chunk in stream:
            yield AiChatResponseFragment(chunk["message"]["content"], is_final=False)

        yield AiChatResponseFragment("", is_final=True)

    def cancel_completion(self) -> None:
        pass
