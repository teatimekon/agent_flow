from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import planner_prompt,task_type,example
from tool import ToolRegistry

class PlannerAgent(BaseAgent):
    def __init__(self, state: AgentState, tool_call: bool = False):
        super().__init__(state=state, tool_call=tool_call)
        
    def invoke(self,user_info:dict, **kwargs):
        user_info = str(user_info)
        question = self.state["question"]
        input_agent_response = self.state["input_agent_response"]
        task_guide_list = self.state["task_guide_list"]
        registered_tools = ToolRegistry.get_all_tools_info()    # 类型是 List[str]
        logger.info(f"\033[0;36m question: {question} \033[0m")
        # 格式化 planner_prompt
        formatted_planner_prompt = planner_prompt.format(
            question=question,
            user_info=user_info,
            task_type=task_type,
            tool_list=registered_tools,
            task_example=example
        )

        messages = [{"role": "user", "content": formatted_planner_prompt}]
        response = self.llm.invoke(messages,json_strict=True, **kwargs)  #大模型输出
        logger.info(f"规划者响应:\n{json.dumps(response, ensure_ascii=False, indent=2)}")
        
        try:
            # plan = json.loads(response.content)
            self.update_state(plan_task_list=response, llm_caller_times=self.get_llm_caller_times())
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            self.update_state(plan_task_list=[], llm_caller_times=self.get_llm_caller_times())
        return self.state
