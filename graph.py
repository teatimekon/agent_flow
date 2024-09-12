from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import Graph, StateType, add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# 定义状态类型
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], StateType.MESSAGES]
    task_list: list[str]

# 定义Task类
class Task(BaseModel):
    description: str
    completed: bool = False

# Input Agent
def input_agent(state):
    last_message = state["messages"][-1]
    return {"messages": state["messages"]}

# Message Agent
def message_agent(state):
    last_message = state["messages"][-1]
    # 这里可以根据需要封装信息
    structured_message = f"封装的信息: {last_message.content}"
    return {"messages": state["messages"] + [AIMessage(content=structured_message)]}

# Planner Agent
def planner_agent(state):
    last_message = state["messages"][-1]
    # 这里可以使用 LLM 来拆解任务
    llm = ChatOpenAI()
    task_list = llm.invoke(f"将以下问题拆解成任务列表: {last_message.content}")
    tasks = [Task(description=task.strip()) for task in task_list.content.split('\n') if task.strip()]
    return {"task_list": [task.dict() for task in tasks]}

# Execute Agent
def execute_agent(state):
    task_list = state.get("task_list", [])
    results = []
    for task in task_list:
        # 这里可以使用 LLM 或其他方法来执行任务
        llm = ChatOpenAI()
        result = llm.invoke(f"执行任务: {task['description']}")
        results.append(result.content)
    
    final_result = "\n".join(results)
    return {"messages": state["messages"] + [AIMessage(content=final_result)]}

# 条件函数
def is_question_a(state):
    last_message = state["messages"][-1]
    return "问题A" in last_message.content

# 构建图
workflow = Graph()

# 添加节点
workflow.add_node("input_agent", input_agent)
workflow.add_node("message_agent", message_agent)
workflow.add_node("planner_agent", planner_agent)
workflow.add_node("execute_agent", execute_agent)

# 添加条件边
workflow.add_conditional_edges(
    "input_agent",
    is_question_a,
    {
        True: "message_agent",
        False: "execute_agent"
    }
)
workflow.add_edge("message_agent", "planner_agent")
workflow.add_edge("planner_agent", "execute_agent")

# 设置入口和出口
workflow.set_entry_point("input_agent")
workflow.set_finish_point("execute_agent")

# 编译图
app = workflow.compile()

# 使用示例
messages = [HumanMessage(content="这是一个测试问题")]
result = app.invoke({"messages": messages})
print(result["messages"][-1].content)
