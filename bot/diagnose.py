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


def export_conversation_history_to_string(
    messages: List[SystemMessage],
) -> str:
    return "\n".join(
        (
            f"User: {msg.content}"
            if isinstance(msg, HumanMessage)
            else f"Assistant: {msg.content}"
            if isinstance(msg, AIMessage)
            else f"ToolMessage called {msg.name}: [context]"
            if isinstance(msg, ToolMessage)
            else ""
        )
        for msg in messages
        if not isinstance(msg, SystemMessage)
    )


class ExpertEnum(str, Enum):
    CARDIOLOGIST = "cardiologist"
    NEUROLOGIST = "neurologist"
    DERMATOLOGIST = "dermatologist"
    GASTROENTEROLOGIST = "gastroenterologist"
    ORTHOPEDIC_SURGEON = "orthopedic surgeon"
    PSYCHIATRIST = "psychiatrist"

class DiagnoseOutputClass(BaseModel):
    is_data_enough_for_initiall_diagnosis = bool = Field(..., description="")
    possible_diseases: list[str] = Field(..., description = "list of possible diseases")
    expert: ExpertEnum = Field(..., description = "which expert is the best to refer to")


structured_llm = llm_model.with_structured_output(DiagnoseOutputClass)
@tool("diagnose_patient")
def diagnose_patient(state: Annotated[dict, InjectedState],):
    """
    Diganose patient and choose wath expertise is needed for this patient to be refered to.
    
    Call this agent to diagnose the patient.
    """
    try:
        #For all key - value in the state["profile"] concat in way "key" - "value"
        profile = "\n".join(
            f"{key}: {value}" for key, value in state.get("profile", {}).items()
        )
        msgs = export_conversation_history_to_string(state["messages"])
        system_prompt = f"""
        You are a highly knowledgeable and responsible virtual medical assistant.
        Your task is to assist with **preliminary (initial) diagnosis** based on the user's described symptoms and history.

        **Important Guidelines:**
        - Your diagnosis is **NOT a final or official medical diagnosis**.
        - Your assessment is ONLY meant to help select the most appropriate medical specialist (e.g., cardiologist, neurologist, dermatologist, etc.) for the user’s next step.
        - DO NOT provide any treatment, medication, or emergency advice.
        - If the user's description is insufficient for even a preliminary assessment, clearly state that more information is needed and set `"is_data_enough_for_initiall_diagnosis": false`.
        - If the description is sufficient, set `"is_data_enough_for_initiall_diagnosis": true`, list the most likely possible diseases (as a shortlist, not a definitive answer), and select the most suitable specialist to refer to (from the allowed list).
        
        This is the profile that we have from the user:
        {profile}

        Use only the information provided in the user's messages and history. If anything is unclear or missing, ask for clarification (if you are allowed), or indicate that data is not enough.
"""
        sys_msg = SystemMessage(content=system_prompt)
        user_msg = HumanMessage(content=msgs)

        results = structured_llm.invoke([sys_msg,user_msg])
        
        return {"tool_answer": results.model_dump()}
    except Exception as e:
        return {"error": "من درحال حاضر به اطلاعات دسترسی ندارم"}
