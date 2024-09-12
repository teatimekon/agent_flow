import yaml
from logs import logger
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
from graph.state import AgentState
from llm import LLMCaller


class BaseAgent:
    def __init__(self, state: AgentState, tool_call: bool = False):
        self.tool_call = tool_call
        self.state = state
        self.llm = LLMCaller(tool_call=self.tool_call)
        
            
    def update_state(self, key, val):
        self.state = {**self.state, key: val}
        

