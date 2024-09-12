from langchain_ollama import ChatOllama
from .BaseLLM import BaseLLM
class Ollama(BaseLLM):
    def __init__(self, model_name: str, tool_call: bool = False):
        super().__init__()
        self.llm = ChatOllama(model=model_name)
        if tool_call:
            self.llm.bind_tools(self.tools)

    def invoke(self, messages, **kwargs):
        return self.llm.invoke(messages)
