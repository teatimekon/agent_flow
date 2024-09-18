import unittest
from tool import ToolRegistry
from tool.tools.get_time_tool import GetTimeToolInput,get_time_tool

from langchain_openai import ChatOpenAI

from config.prompt_cn import task_to_langchain_prompt

dependency_task_output = ""
question = "北京昨天的天气怎么样"
task_description = "获取当前日期"

from llm import LLMCaller

llm = LLMCaller(tool_call=True)
prompt = task_to_langchain_prompt.format(question=question,task_description=task_description,dependency_task_output=dependency_task_output)
ai_msg = llm.invoke(prompt)

print(ai_msg)

messages = []
for tool_call in ai_msg.tool_calls:
    selected_tool = ToolRegistry._tools[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

print(messages)


