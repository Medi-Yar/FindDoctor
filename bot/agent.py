from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from bot.tools import find_doctor, diagnose_patient
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize model with tool support
# model = ChatOpenAI(model="gpt-4o", temperature=0)
model = ChatOpenAI(
    model_name="openai/gpt-4.1-mini",
    openai_api_base=LLM_BASE_URL,
    openai_api_key=OPENROUTER_API_KEY,
    temperature=0.2,
)

tools = [find_doctor, diagnose_patient]

model_with_tools = model.bind_tools(tools)

sys_prompt = f"""
                You are a great medical Assistant. You will help user find a suitable doctor to help them with their ailments.
                You should try to diagnose the sickness (and relevant medical expertise) first, unless user says what kind of doctor they need.
                You should ask follow up questions if your try at diagnoses fails.
                You should search for a suitable doctor according to the user's need
                You should Search again if user doesn't want the recommended doctor
            """

sys_msg = SystemMessage(content=sys_prompt)


# Node
def assistant(state: MessagesState):
    msg_history = state["messages"]
    new_msg = model_with_tools.invoke([sys_msg] + msg_history)
    return {"messages": new_msg}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph_no_memory = builder.compile()



