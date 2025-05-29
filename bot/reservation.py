from typing import Literal, Annotated
from pydantic import BaseModel, Field
from langchain.tools import tool
import warnings
import json
from typing import Literal
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, RemoveMessage, ToolMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import InjectedState

from langchain_openai import ChatOpenAi

llm_model = ChatOpenAi(name="gpt-4.1-mini")


class ReserveApointment(BaseModel):
    date: str
    time: str
    phone_number: str
    doctor_id: str


@tool("diagnose_patient", args_schema=ReserveApointment)
def context_retriever(date, time, phone_number, doctor_id):
    """
    Reserve Time for patient when doctor is specificaly determined.
    """
    try:
        return {
            "message": "Time Reserverd",
            "info": {
                "date": date,
                "time": time,
                "phone_number": phone_number
            }
        }
    except Exception as e:
        return {"error": "من درحال حاضر به اطلاعات دسترسی ندارم"}
