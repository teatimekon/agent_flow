from graph.RouterNode import RouterNode
from graph.state_new import AgentState
from agent import Agent
from config.preprint import Colors
from langchain_core.tools import tool
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

@tool   
def handle_kodo_question():
    """ 
    处理kodo相关的问题
    """
    print(f"{Colors.OKBLUE}handle_kodo_question{Colors.ENDC}")
    return "kodo_agent"

@tool
def handle_cdn_question(question:str):
    """ 
    处理cdn相关的问题
    """
    print(f"{Colors.OKBLUE}handle_cdn_question{Colors.ENDC}",question)
    return "cdn_agent"

kodo_agent = Agent(name="kodo_agent",
                   model="gpt-4o-mini",
                   tools=[handle_kodo_question],
                   instruction="你是kodo的专家，能处理kodo相关的问题，例如：如何上传文件到kodo，如何下载文件到kodo，如何删除文件到kodo，如何查询文件到kodo")
cdn_agent = Agent(name="cdn_agent",
                  model="gpt-4o-mini",
                  tools=[handle_cdn_question],
                  instruction="你是cdn的专家，能处理cdn相关的问题，例如：如何配置cdn，如何查询cdn，如何删除cdn，如何添加cdn")
router = RouterNode(agent_list=[kodo_agent,cdn_agent])

graph = StateGraph(AgentState)
graph.add_node("RouterNode",router.invoke)
graph.add_edge("RouterNode",END)
graph.add_edge(START,"RouterNode")
memory = MemorySaver()
graph = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


while True:
    question = input("请输入问题：")
    ans = graph.invoke({"question": question},config=config)
    for message in ans["messages"]:
        message.pretty_print()
    