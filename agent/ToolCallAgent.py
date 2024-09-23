from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import planner_prompt,task_type,example
from tool import ToolRegistry
from langchain_core.messages import ToolMessage

class ToolCallAgent(BaseAgent):
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        
    def invoke(self, **kwargs):
        tool_response = self.state["messages"][-1].tool_calls[0]
        print("tool_response: ", tool_response)    
        selected_tool = ToolRegistry._tools[tool_response['name'].lower()]
        tool_msg = selected_tool.invoke(tool_response)
        print(tool_msg)
        return {"messages": [tool_msg]}