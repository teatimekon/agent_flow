from graph.state import AgentState
from .BaseAgent import BaseAgent
import json
from logs import logger
from config.prompt import gateway_prompt
class InputAgent(BaseAgent):

    def invoke(self,question: str, **kwargs):
        prompt = gateway_prompt.format(user_query=question)
        messages = [{"role": "user", "content": prompt}]
        ai_msg = self.llm.invoke(messages, **kwargs)
        response = ai_msg.content
        logger.info(f"Response: {response}, type: {type(response)}")
        # 解析大模型的输出
        try:
            self.update_state(input_agent_response=response)
            return self.state
            
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            logger.debug(f"LLM response: {ai_msg}")
            error_response = """{
                "directly_answer": True,
                "explain": "无法解析大模型响应",
                "product": "未知"
            } """
            
            self.update_state(input_agent_response=error_response, llm_caller_times=self.get_llm_caller_times())
            return self.state
            