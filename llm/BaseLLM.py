from tool import ToolRegistry
from langchain_core.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchResults
from logs import logger
from langchain.agents import Tool
class BaseLLM:
    def __init__(self):
        self.tools = self.init_tools()
        self.llm = None
    
    def init_tools(self):
        tools = ToolRegistry.get_langchain_tools()
        return tools
    
    # def register_tool(self, *tools: BaseTool):   
    #     for tool in tools:
    #         if tool not in self.tools:
    #             self.tools.append(tool)
    
    # def remove_tool(self,tool:BaseTool):
    #     if tool in self.tools:
    #         self.tools.remove(tool)
    #     else:
    #         logger.error(f"Tool {tool.name} not found")
    #     return self.tools
    
    def get_llm(self):
        return self.llm
    
