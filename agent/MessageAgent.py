from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import message_guide,task_type
class MessageAgent(BaseAgent):
    def __init__(self,user_info:dict,state:AgentState):
        super().__init__(state=state)
        self.user_info = str(user_info)

    def invoke(self):
        input_agent_response = self.state["input_agent_response"]
        question = self.state["question"]
        planner_prompt = message_guide.format(task_type_list=task_type)
        # planner_prompt = f"{self.prompt_config['prompt']['planner']}"
        planner_prompt += f"下面是用户的信息，这也是你规划问题需要考虑的因素：{self.user_info}"
        planner_prompt += f"\n下面是用户的问题：{question}"
        logger.info(f"planner_prompt: {planner_prompt}")
        res = self.llm.invoke(planner_prompt).content
        logger.info(f"res: {res}")
        task_guide_list = json.loads(res)
        self.update_state({"task_guide_list":task_guide_list, "llm_caller_times": self.get_llm_caller_times()})
        return self.state

