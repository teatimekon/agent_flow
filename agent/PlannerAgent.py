from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import planner_prompt,task_type,example
from tool import ToolRegistry

class PlannerAgent(BaseAgent):
    def __init__(self, state: AgentState):
        super().__init__(state=state)

    def invoke(self,user_info:dict, **kwargs):
        user_info = str(user_info)
        question = self.state["question"]
        input_agent_response = self.state["input_agent_response"]
        task_guide_list = self.state["task_guide_list"]
        registered_tools = ToolRegistry.get_all_tools_info()    # 类型是 List[str]
        
        # 格式化 planner_prompt
        formatted_planner_prompt = planner_prompt.format(
            question=question,
            user_info=user_info,
            task_type=task_type,
            tool_list=registered_tools,
            task_example=example
        )

        messages = [{"role": "user", "content": formatted_planner_prompt}]
        response = self.llm.invoke(messages, **kwargs)

        logger.info(f"Planner response: {response.content}")

        try:
            plan = json.loads(response.content)
            self.update_state("plan_task_list", plan)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            self.update_state("plan_task_list", [])


        return self.state
