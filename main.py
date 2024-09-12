from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage
from langchain_community.tools import DuckDuckGoSearchResults
from tool import get_time
from llm import LLMCaller
@tool
def get_weather(location: str):
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."


@tool
def get_coolest_cities():
    """Get a list of coolest cities"""
    return "nyc, sf"

class GetWeather(BaseModel):
    """Get the current weather in a given location"""

    location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0,base_url="https://api2.aigcbest.top/v1",api_key="sk-WbEpTniVLtZbePrk3e4fE2B1AbCd43B6B0FcCaC5A0478934")
myLLMCaller = LLMCaller(tool_call=True)


tools = [get_weather,get_coolest_cities]
# llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)



# ai_msg = tool_node.invoke({"messages": [message_with_single_tool_call]})

ai_msg = myLLMCaller.invoke(
    "what is the weather in beijing,if you don't know,help me search it on the internet",
)
print(ai_msg)