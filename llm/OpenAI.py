from langchain_openai import ChatOpenAI
from .BaseLLM import BaseLLM

class OpenAI(BaseLLM):
    def __init__(self, model_name: str, api_key: str = None, base_url: str = None, tool_call: bool = False):
        super().__init__()
        self.llm = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
        if tool_call:
            self.llm = self.llm.bind_tools(self.tools,strict=True)
        
    def invoke(self, messages, **kwargs):
        if "must_call" in kwargs:
            must_call_tool_llm = self.llm.bind_tools(self.tools,strict=True,tool_choice='any')
            print("调用了must_call_tool_llm")
            return must_call_tool_llm.invoke(messages)
        return self.llm.invoke(messages)
    