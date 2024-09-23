
from typing import TypedDict, Annotated, Literal


from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from tool import ToolRegistry
from llm import LLMCaller

memory = MemorySaver()
llm = LLMCaller()

class AgentState(TypedDict):
    messages: Annotated[list,add_messages]
    tool_messages: Annotated[list,add_messages]

def call_tool(state: AgentState):
    """
    调用用工具得到返回结果（call api步骤）
    """
    tool_response = state["messages"][-1].tool_calls[0]
    print("tool_response: ", tool_response)    
    selected_tool = ToolRegistry._tools[tool_response['name'].lower()]
    tool_msg = selected_tool.invoke(tool_response)
    
    print(tool_msg)
    return {"messages":[tool_msg]}

def call_llm(state: AgentState):
    """
    调用语言模型得到返回结果
    """
    print("call_llm: ",state["messages"])
    llm_response = llm.invoke(messages=state["messages"],tool_call=True)
    print("llm_response: ",llm_response)
    return {"messages":[llm_response]}

def should_call_tool(state: AgentState):
    """
    判断是否需要调用工具
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0 :
        print("to call_tool")
        return "call_tool"
    print("to end")
    return END

graph_builder = StateGraph(AgentState)
graph_builder.add_node("call_llm",call_llm)

graph_builder.add_node("call_tool",call_tool)

graph_builder.add_conditional_edges(
    "call_llm",
    should_call_tool,
    {"call_tool":"call_tool",END: END}
)

graph_builder.add_edge("call_tool","call_llm")
graph_builder.add_edge(START,"call_llm")

graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    output = graph.invoke({"messages": [("user", user_input)]}, config=config)
    print("output: ",output)
    for message in output["messages"]:
        message.pretty_print()