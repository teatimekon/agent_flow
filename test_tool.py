import unittest
from tool import ToolRegistry
from tool.tools.get_time_tool import GetTimeToolInput,get_time_tool

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", api_key="sk-WbEpTniVLtZbePrk3e4fE2B1AbCd43B6B0FcCaC5A0478934", base_url="https://api2.aigcbest.top/v1")
print(get_time_tool)
llm.bind_tools([get_time_tool])

print(ToolRegistry.get_tool("get_time_tool"))
print(ToolRegistry.get_langchain_tools())



