from llm.LLMCaller import LLMCaller
from tool.tool_registry import ToolRegistry
from langchain_core.tools import tool

def test_llm_caller_refresh_tools():
    # 初始化 LLMCaller
    llm_caller = LLMCaller(tool_call=True)
    
    # 获取初始工具数量
    initial_tool_count = len(llm_caller.tools)
    print(f"初始工具数量: {initial_tool_count}")
    
    # 定义新工具
    @tool
    def new_test_tool(input: str) -> str:
        """一个用于测试的新工具"""
        return f"新工具处理了输入: {input}"
    
    # 注册新工具
    ToolRegistry.register(new_test_tool)
    
    # 刷新 LLMCaller 中的工具
    llm_caller.refresh_tools()
    
    # 获取刷新后的工具数量
    refreshed_tool_count = len(llm_caller.tools)
    print(f"刷新后工具数量: {refreshed_tool_count}")
    
    # 检查工具数量是否增加
    print(f"工具数量是否增加: {refreshed_tool_count > initial_tool_count}")
    
    # 检查新工具是否在刷新后的工具列表中
    tool_names = [tool.name for tool in llm_caller.tools]
    print(f"新工具 'new_test_tool' 是否在工具列表中: {'new_test_tool' in tool_names}")
    
    # 打印所有工具名称
    print("刷新后的所有工具名称:")
    for name in tool_names:
        print(f"- {name}")

if __name__ == '__main__':
    test_llm_caller_refresh_tools()