import os
import chainlit as cl
from dotenv import load_dotenv
from bot.agent import react_graph_no_memory, react_graph_memory
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage


load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# model = ChatOpenAI(model_name="google/gemini-2.5-flash-preview", openai_api_base=LLM_BASE_URL, openai_api_key=OPENROUTER_API_KEY, temperature=0)

# graph = build_chatbot_app(model, [])
graph = react_graph_no_memory
graph = react_graph_memory


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    # await cl.Message(content=graph.invoke({"messages": [msg.content]}, config=config)["messages"][-1].content).send()
    cb = cl.LangchainCallbackHandler()
    final_answer = cl.Message(content="")
    
    for msg, metadata in graph.stream({"messages": [HumanMessage(content=msg.content)]}, stream_mode="messages", config=RunnableConfig(callbacks=[cb], **config)):
        if (
            msg.content
            and not isinstance(msg, HumanMessage) and not isinstance(msg, ToolMessage)
        ):
            await final_answer.stream_token(msg.content)

    await final_answer.send()

