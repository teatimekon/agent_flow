import unittest
from tool import ToolRegistry
from tool.tools.get_time_tool import GetTimeToolInput,get_time_tool


question = "我在服务器 333下载 xxx.txt文件时出错了,我id 是 123"

from llm import LLMCaller

llm = LLMCaller()
prompt = "你是一个工具调用大师，你一定要选择一个工具进行调用，根据用户提供的信息和工具的描述构造工具需要的参数，如果用户没提供或者没提供完全，对应的参数置空就行，你继续调用该工具，用户的问题是："


while True:
    ai_msg = llm.invoke(messages=question,tool_call=True)

    print(ai_msg)

    messages = []
    for tool_call in ai_msg.tool_calls:
        selected_tool = ToolRegistry._tools[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)

    print(messages)


