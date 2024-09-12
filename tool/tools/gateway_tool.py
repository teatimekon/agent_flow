#判断输入是否合理
from langchain_core.tools import tool
from tool import ToolRegistry  # 修改这里
from typing import Annotated
from pydantic import BaseModel, Field

class GatewayToolInput(BaseModel):
    """
    useful when you need to check if the input is a valid input
    """
    query: str = Field(description="The query to check if it is a valid input")


@ToolRegistry.register
@tool("gateway_tool",args_schema=GatewayToolInput)
def gateway_tool(query: str) -> str:
    
    return "True"