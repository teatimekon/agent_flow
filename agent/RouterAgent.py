from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import planner_prompt,task_type,example
from tool import ToolRegistry
from langchain_core.messages import ToolMessage,SystemMessage
class UpDownloadAgent(BaseAgent):
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        self.sop_prompt = """
        如果用户需要上传文件，你将调用上传文件的工具，如果用户需要下载文件，你将调用下载文件的工具。
        如果同时上传和下载，你将一步一步调用工具，指引用户一步步完成。一次只执行一个工具.
        """
        
    def invoke(self, **kwargs):
        # sys_prompt = SystemMessage(content=self.sop_prompt)
        # if sys_prompt not in self.state["messages"]:
        #     self.state["messages"].append(sys_prompt)
        question = self.state["question"]
        question = {"role": "user", "content": question}
        history_messages = self.state["messages"]
        for msg in history_messages:    
            print(f"\033[94m{msg}\033[0m")
        if len(self.state["messages"]) > 0 and type(self.state["messages"][-1]) == ToolMessage:
            ai_msg = self.llm.invoke(messages=history_messages,**kwargs)
        else:
            ai_msg = self.llm.invoke(messages=history_messages + [question], tool_call=self.tool_call,**kwargs)
        print("ai_msg: ", ai_msg)
        return {"messages": [question, ai_msg]}