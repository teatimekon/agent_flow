from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import planner_prompt,task_type,example
from tool import ToolRegistry

class EvaluateAgent(BaseAgent):
    #拿到执行agent 的评估输出进行处理
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        
    
    def invoke(self):
        execute_agent_result = self.state["execute_agent_result"]
        pass