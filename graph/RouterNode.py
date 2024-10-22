from typing import Callable
from agent import Agent
from graph.state_new import AgentState
from config.prompt_class import Prompt
from llm_new.llm_caller import LLMCaller
from langchain_core.tools import tool,StructuredTool,BaseTool
from config.preprint import Colors
import json

class RouterNode():
    def __init__(self,agent_list:list[Agent]):
        self.agent_list:list[Agent] = agent_list
        self.agent_map:dict[str,Agent] = {agent.name: agent for agent in self.agent_list}
        self.sop_prompt = Prompt.get_prompt(name="router")
        self.transfer_agent_function_map = {}
        self.llm_caller = LLMCaller(tools=self.get_transfer_agent())
        self.is_initialized = True  #判断是否加上 system prompt，在初始化后的第一条消息前加上 system prompt
        
    def get_agent(self,agent_name:str):
        return self.agent_map.get(agent_name,None)
        
    def invoke(self,state:AgentState):
        # 在这个节点只负责路由到哪个 agent 进行工作
        
        query = [{"role": "user", "content": "用户的问题是：" + state["question"]}]
        if self.is_initialized:     #笨蛋写法
            self.is_initialized = False
            query = [{"role": "system", "content": self.sop_prompt}] + query
        history = state["messages"]
        for message in history:
            message.pretty_print()
        router_input = history + query 
        print(f"{Colors.GREY}router_input: {router_input}{Colors.ENDC}")
        for i in history+router_input:
            print(i)
        ai_msg = self.llm_caller.invoke(messages=router_input,tool_call=True,parallel_tool_calls=False)
        
        message = router_input + [ai_msg]
        
        print(f"{Colors.RED}ai_msg: {ai_msg}{Colors.ENDC}")
        next_agent = ""
        if hasattr(ai_msg, "tool_calls") and len(ai_msg.tool_calls) > 0:
            # 如果 ai_msg 有 tool_calls， 调用 function拿到转移到对应的 agent
            tool_call =  ai_msg.tool_calls[0]
            print("tool_call",tool_call)
            func_name = tool_call["name"]
            args = tool_call["args"]
            agent = self.transfer_agent_function_map[func_name].invoke(args)
            next_agent = agent.name
            tool_message = {
                "tool_call_id": tool_call["id"],
                "role": "tool",
                "name": func_name,
                "content": f"Transferred to {next_agent} agent"
            }
            message.append(tool_message)
        
        return {'messages': message,'next_agent': next_agent}
    
    def get_transfer_agent(self):
        tools = []
        for agent in self.agent_list:
            agent_name = "_".join(agent.name.split("_")[:-1])
            print("agent_name",agent_name)
            func_name = f"transfer_to_{agent_name}"
            func_doc = f"将用户的问题转移到处理 {agent_name} 问题的 agent,该 agent 的能力是：{agent.instruction}"
            
            def transfer_func():
                return agent

            transfer_func = StructuredTool.from_function(transfer_func,name=func_name,description=func_doc)
            print("transfer_func",transfer_func)
            self.transfer_agent_function_map[transfer_func.name] = transfer_func
            tools.append(transfer_func)
            print(type(transfer_func))
        return tools
    
