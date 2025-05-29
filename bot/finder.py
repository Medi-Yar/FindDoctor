from typing import Literal, Annotated
from pydantic import BaseModel, Field
from langchain.tools import tool
import warnings
import json
from typing import Literal, List
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, RemoveMessage, ToolMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import InjectedState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage


from langchain_openai import ChatOpenAi

llm_model = ChatOpenAi(name="gpt-4.1-mini")




structured_llm = llm_model.with_structured_output(DoctorInfoCard)
@tool("find_doctor")
def find_doctor(state: Annotated[dict, InjectedState],):
    try:
        
        return {"tool_answer": results.model_dump()}
    except Exception as e:
        return {"error": "من درحال حاضر به اطلاعات دسترسی ندارم"}
