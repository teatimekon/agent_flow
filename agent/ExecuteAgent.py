from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger

class Task:
    def __init__(self, task_name:str, task_description:str, task_type:str, task_dependency:list[int]):
        self.task_name = task_name
        self.task_description = task_description
        self.task_type = task_type
        self.tast_dependency = task_dependency
        

class ExecuteAgent(BaseAgent):
    def invoke(self):
        plan_task_list = self.state["plan_task_list"]
        for task in plan_task_list:
            # 执行任务
            pass
        return self.state