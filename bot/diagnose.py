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


class RetrieveContextInputs(BaseModel):
    question: str = Field(description="Query")


class ExpertEnum(str, Enum):
    CARDIOLOGIST = "cardiologist"
    NEUROLOGIST = "neurologist"
    DERMATOLOGIST = "dermatologist"
    GASTROENTEROLOGIST = "gastroenterologist"
    ORTHOPEDIC_SURGEON = "orthopedic surgeon"
    PSYCHIATRIST = "psychiatrist"

class DiagnoseOutputClass(BaseModel):
    possible_diseases: list[str] = Field(..., description = "list of possible diseases")
    expert: ExpertEnum = Field(..., description = "which expert is the best to refer to")


structured_llm = llm_model.with_structured_output(DiagnoseOutputClass)
@tool("diagnose_patient", args_schema=RetrieveContextInputs)
def context_retriever(state: Annotated[dict, InjectedState],):
    """
    Diganose patient and choose wath expertise is needed for this patient to be refered to.
    
    Call this agent to diagnose the patient.
    """
    try:
        system_prompt = f"""
        You are a real good doctor that can tell the sickness and who to refer to. help the user.
        """

        results = structured_llm.invoke(system_prompt + state["messages"] + HumanMessage("Can You Tell me my diagnoses?"))
        
        return {"tool_answer": results.model_dump()}
    except Exception as e:
        return {"error": "من درحال حاضر به اطلاعات دسترسی ندارم"}
