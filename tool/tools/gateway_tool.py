#判断输入是否合理
from langchain_core.tools import tool
from tool import ToolRegistry  # 修改这里
from typing import Annotated
from pydantic import BaseModel, Field

class GatewayToolInput(BaseModel):
    """
    检查输入的问题是否与七牛云相关，输出是是否与七牛云相关
    """
    query: str = Field(description="用户的原始输入")


@ToolRegistry.register
@tool("gateway_tool",args_schema=GatewayToolInput)
def gateway_tool(query: str) -> str:
    
    return "True"