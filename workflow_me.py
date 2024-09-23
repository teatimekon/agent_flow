from agent import UpDownloadAgent,ToolCallAgent
from graph.state import AgentState

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

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
        return "ToolCallAgent"
    print("to end")
    return END

graph = StateGraph(AgentState)

graph.add_node("UpDownloadAgent",
               lambda state: UpDownloadAgent(
                    state=state,tool_call=True
                       ).invoke()
               )

graph.add_node("ToolCallAgent",
               lambda state: ToolCallAgent(state=state).invoke())


graph.add_conditional_edges(
    "UpDownloadAgent",
    should_call_tool,
    {"ToolCallAgent":"ToolCallAgent",END: END}
)

graph.add_edge("ToolCallAgent","UpDownloadAgent")
graph.add_edge(START,"UpDownloadAgent")

memory = MemorySaver()
graph = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

while True:
    
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        break
    output = graph.invoke({"question": user_input}, config=config)
    print("output: ",output)
    for message in output["messages"]:
        message.pretty_print()