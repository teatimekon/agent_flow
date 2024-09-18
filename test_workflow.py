from agent import InputAgent,MessageAgent,PlannerAgent,ExecuteAgent
from graph.state import AgentState

from langgraph.graph import StateGraph,START,END

graph = StateGraph(AgentState)

graph.add_node(
    "input_agent",
    lambda state: InputAgent(
        state=state,
        tool_call=True
    ).invoke(
        question=state["question"],
    )
)
# graph.add_node(
#     "message_agent",
#     lambda state: MessageAgent(
#         state=state,
#         user_info={"name":"张三","age":18,"gender":"male","email":"zhangsan@example.com","phone":"13800138000","address":"北京市海淀区"
#                    ,"company":"阿里巴巴","position":"高级工程师","department":"技术部","department_leader":"李四","department_leader_email":"lisi@example.com","department_leader_phone":"13800138001","department_leader_address":"北京市海淀区"}
#     ).invoke()
# )
graph.add_node(
    "planner_agent",
    lambda state: PlannerAgent(
        state=state,
        tool_call=True
    ).invoke(
        user_info={"name":"张三","age":18,"gender":"male","email":"zhangsan@example.com","phone":"13800138000","address":"北京市海淀区"
                   ,"company":"阿里巴巴","position":"高级工程师","department":"技术部","department_leader":"李四","department_leader_email":"lisi@example.com","department_leader_phone":"13800138001","department_leader_address":"北京市海淀区"}
    )
)
graph.add_node(
    "execute_agent",
    lambda state: ExecuteAgent(
        state=state,
        tool_call=True
    ).invoke()
)

graph.set_entry_point("input_agent")


graph.add_edge("input_agent","planner_agent")
graph.add_edge("planner_agent","execute_agent")
graph.add_edge("execute_agent",END)

workflow = graph.compile()

res = workflow.invoke({"question":"一位农夫带着一头狼，一只羊和一筐白菜过河，河边有一条小船，农夫划船每次只能载狼、羊、白菜三者中的一个过河。农夫不在旁边时，羊会喜欢狼，狼会喜欢白菜。问农夫该如何过河"})
#action 的问题，具体如何执行，需要 tool 接入 exp：
print(res)

print(res["llm_caller_times"])
