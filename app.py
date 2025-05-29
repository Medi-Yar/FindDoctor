from typing import Literal
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import HumanMessage

import chainlit as cl
from bot.main_bot import build_chatbot_app


model = ChatOpenAI(model_name="google/gemini-2.5-flash-preview", openai_api_base="https://openrouter.ai/api/v1", openai_api_key="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", temperature=0)

graph = build_chatbot_app(model, [])

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import MessagesState
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    await cl.Message(content=graph.invoke({"messages": [msg.content]}, config)["messages"][-1].content).send()
