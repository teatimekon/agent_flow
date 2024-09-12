from typing import Annotated, Sequence
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    question: str
    input_agent_response: Annotated[list, add_messages] # 由InputAgent生成
    message_agent_response: Annotated[list, add_messages] 
    task_guide_list: list   # 由MessageAgent生成
    plan_task_list: list    # 由PlannerAgent生成
    # should_retry_planner: bool  # 如果计划任务列表出错，则需要重试
# state = {
#     "question": "",
#     "input_agent_response": []
# }