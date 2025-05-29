from typing import Literal
from pydantic import BaseModel, Field
from langchain.tools import tool
import warnings
import json
from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, RemoveMessage, ToolMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver


def build_chatbot_app(
    llm_model,
    list_of_tools,
):
    # checkpointer = memorySaver()

    warnings.filterwarnings('ignore')



    # Bind tools to model
    real_model_with_tools = llm_model.bind_tools(list_of_tools)



   
    # Main conversation node
    def call_model(state):

        system_message = f"""
        
            """
        


        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = real_model_with_tools.invoke(messages)
        return {"messages": [response]}


    def should_continue(state) -> Literal["summarize_conversation", END]:
            messages = state.get("messages", [])
            ai_message = messages[-1]
            if hasattr(ai_message, "tool_calls") and ai_message.tool_calls:
                return "tools"
            if len(messages) > 12:
                return "summarize_conversation"
            return END
    class BasicToolNode:
        """A node that runs the tools requested in the last AIMessage."""

        def __init__(self, tools: list) -> None:
            self.tools_by_name = {tool.name: tool for tool in tools}

        def __call__(self, inputs: dict):
            if messages := inputs.get("messages", []):
                message = messages[-1]
            else:
                raise ValueError("No message found in input")
            outputs = []
            
            for tool_call in message.tool_calls:
                try:
                    # Use the context_retriever tool directly
                    tool_args = tool_call["args"]
                    result = self.tools_by_name[tool_call["name"]].invoke(tool_args)
                    outputs.append(
                        ToolMessage(
                            content=json.dumps(result, ensure_ascii=False),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
                except Exception as e:
                    logger.error(f"An error occurred: {e}")
                    outputs.append(
                        ToolMessage(
                            content=json.dumps({"error": "Could Not Retrieve. Try Again."}, ensure_ascii=False),
                            name=tool_call["name"],
                            tool_call_id=tool_call["id"],
                        )
                    )
            return {"messages": outputs, "used_tool": tool_call["name"]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("tools", BasicToolNode(tools=[context_retriever]))
    workflow.add_node("conversation", call_model)
    workflow.add_edge(START, "conversation")
    workflow.add_conditional_edges(
        "conversation",
        should_continue,
        {"tools": "tools", "summarize_conversation": "summarize_conversation", END: END},
    )
    workflow.add_edge("tools", "conversation")
    workflow.add_edge("summarize_conversation", END)

    # Compile and return the multi-agent RAG app
    return workflow.compile(checkpointer=checkpointer)
