from langchain_core.tools import tool, InjectedToolCallId
import os
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
# from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import InjectedState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


load_dotenv()


LLM_BASE_URL = os.getenv("LLM_BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

from paziresh24_interface.paziresh24_utils import get_doctor_list, get_doctor_details, async_get_doctor_details


class FindDoctorInputSchema(BaseModel):
    """Schema to get a list of doctors based on various filters."""
    
    text: Optional[str] = Field(None, description="Search text (symptom, disease, or expertise)")
    
    city: Literal["abbar", "abadan", "abadeh", "abdanan", "abegarm", "abyek", "azarshahr", "aran-va-bidgol", "azadshahr", "asara", "astara", "astaneh-ye-ashrafiyeh", "ashtian", "ashkhaneh", "aghajari", "aq-qala", "amol", "avej", "abarkooh", "abu-musa", "abhar", "arak", "ardabil", "ardestān", "ardakan", "ardakan-fars", "ardal", "arsenjan", "orumieh", "azna", "estahban", "asadabad", "esfarāyen", "osku", "eslamabad-e-gharb", "eslamshahr", "eshtehard", "ashkezar", "oshnavieh", "isfahan", "eghlid", "aleshtar", "alvand", "aligudarz", "amlash", "omidiyeh", "anar", "andisheh", "andimeshk", "gouharan", "ahar", "ahram", "ahvaz", "ijrud", "izeh", "iranshahr-khuzestan", "iranshahr", "ilam", "ilkhchi", "iwan", "eyvanakey", "bab-anar", "babak", "babol", "babolsar", "basmenj", "basht", "baghbahadoran", "baghmalek", "baft", "bafgh", "baghershahr", "baneh", "bajestan", "bojnurd", "borazjan", "bord-khun", "bardaskan", "bardsir", "borujerd", "borujen", "bostanabad", "bastak", "bastam", "boshruyeh", "baladeh", "bam", "bonab", "bandar-imam-khomeini", "bandar-e-jask", "bandar-khamir", "kiashahr", "bandar-gaz", "bandar-lengeh", "bandar-mahshahr", "bandar-anzali", "bandar-abbas", "bavanat", "buin-zahra", "bushehr", "bukan", "boomehen", "bahar", "behbahan", "behshahr", "bijar", "birjand", "beyza", "bileh-savar", "parsabad", "parsian", "pasargad", "pakdasht", "pave", "pol-sefid", "pol-dokhtar", "poldasht", "piranshahr", "takestan", "talesh", "taybad", "tabriz", "tajrish", "torbat-e-jam", "torbat-heydariyeh", "torkaman", "tasuj", "taft", "tafresh", "takab", "tonekabon", "tangestan", "tuyserkan", "tehran", "tiran", "jajarm", "jolfa", "jam", "javanrud", "juybar", "jahrom", "jiroft", "chabahar", "chadegan", "chaldoran", "chalus", "qarah-ziyaeddin", "chelgerd", "chenaran", "chahar-dangeh", "haji-abad", "haji-abad-isfahan", "haji-abad-fars", "hasan-abad", "hamidiyeh", "hamidiyeh-shahr", "kharg", "khash", "khodabandeh", "kharameh", "khorramabad", "khorrambid", "khorramdarreh", "khorramshahr", "khosroshahr", "khoshkebijar", "khalkhal", "khomam", "khomein", "khomeini-shahr", "khonj", "khaf", "khansar", "khormoj", "khoy", "darab", "damghan", "dorcheh", "dargaz", "darmiyan", "darreh-shahr", "dezful", "dezful-lorestan", "dashtestan", "dashti", "delijan", "damavand", "dana", "dorud", "dogonbadan", "dowlatabad", "dehaghan", "dehbārez", "dehdasht", "dehloran", "dayyer", "bandar-deylam", "divandarreh", "rask", "ramsar", "ramshir", "ramhormoz", "ramian", "ravar", "robat-karim", "razan", "rasht", "rezvanshahr", "rafsanjan", "ravansar", "rudsar", "rudbar", "roodehen", "shahr-e-rey", "zabol", "zarch", "zahedan", "zarghan", "zarand", "zarinabad", "zarinshahr", "zanjan", "sari", "saman", "saveh", "sabzevar", "sepidan", "sarpol-zahab", "sardasht", "sarab", "sarableh", "saravan", "sarbaz", "sarbishe", "sarakhs", "sarein", "sarvestan", "saqqez", "salmas", "salmanshahr", "semnan", "semirom", "sonqor", "sanandaj", "savadkuh", "surian", "susangerd", "sahand", "sisakht", "siahkal", "sirjan", "sirik", "siah-cheshmeh", "shadegan", "shazand", "shandiz", "shahediyeh", "shahroud", "shahin-dej", "shahin-shahr", "shabestar", "sharifabad", "shaft", "shush", "shushtar", "showt", "shahreza", "shahrekord", "shahriar", "shiraz", "shirvan", "sahneh", "safashahr", "someh-sara", "tarom", "taleqan", "tabas", "tabas-masina", "tabas-yazd", "torghabeh", "ajabshir", "asaluyeh", "alavijeh", "aliabad-e-katul", "farsan", "faruj", "famenin", "farashband", "ferdows", "fereidan", "fereydun-shahr", "fereydunkenar", "fariman", "fasa", "fasham", "felard", "falavarjan", "fooladshahr", "fooman", "firuzabad", "firuzkuh", "firooze", "qaemshahr", "ghaemiyeh", "ghayen", "qaderabad", "qods", "qarchak", "qorveh", "ghareaghaj", "qazvin", "qeshm", "qasr-e-shirin", "qom", "ghochan", "qohestan", "qeydar", "ghirokarzin", "kazeroon", "kashan", "kashmar", "kaki", "kamyaran", "kabudrahang", "karaj", "kordkuy", "kerman", "kermanshah", "kalat-nader", "kelachay", "kalaleh", "kaleybar", "kan", "kandovan", "bandar-e-kangan", "kangavar", "kavar", "kosar", "kouhbanan", "kuhpayeh", "kuhdasht", "kahrizak", "kahnooj", "kiar", "kish", "kivi", "gachsaran", "gerash", "gorgan", "garmsar", "garmeh", "germi", "golpayegan", "gonabad", "bandar-ganaveh", "gonbad-kavus", "gohardasht", "gilan-gharb", "lar", "lali", "lamerd", "lahijan", "lordegan", "lasht-e-nesha", "langarud", "lavasan", "likak", "masal", "masuleh", "maku", "mahdasht", "mahshahr", "mahneshan", "mobarakeh", "mahalat", "mohammadieh", "mahmudabad", "maragheh", "marand", "marvdasht", "mariwan", "masjed-soleiman", "meshkindasht", "meshgin-shahr", "mashhad", "mollasani", "malard", "malayer", "malekan", "mamasani", "mamaghan", "manjil", "mahabad", "mehr", "mehran", "mehriz", "qoshachay", "mianeh", "meybod", "mirjaveh", "minab", "minudasht", "naein", "najafabad", "natanz", "nazarabad", "naqadeh", "neka", "namin", "nur", "nourabad", "nurabad", "nowshahr", "nahavand", "nehbandan", "neyriz", "nir", "neyshabur", "nikshahr", "varamin", "varzeghan", "varzaneh", "hadishahr", "herat", "harsin", "heris", "hashtpar", "hashtrood", "hashtgerd", "hamedan", "hendijan", "hoveyzeh", "yasuj", "yazd"] = Field("tehran", description='City to get the doctor list from')
    
    expertise: Optional[Literal["orthopedics", "obstetrics-gynecology", "ophthalmology", "gastroenterology", "urology", "endocrinology", "cardiovascular", "internal", "dental-oral", "dermatology", "surgery", "pediatrics", "psychiatry", "pulmonology", "otorhinolaryngology", "general-practitioner", "corona-virus", "rehabilitation", "anesthesia-and-intensive-care", "nutrition", "neurology", "psychology", "palliative-care", "infectious", "beauty", "oncology", "imaging", "diabetes", "pharmacology", "traditional-medicine", "genetics", "allergies", "laboratory-and-imaging", "emergency-medicine", "sexual-health"]] = Field(None, description='Doctor\'s expertise')
    sub_expertise: Optional[str] = Field(None, description="Doctor's sub-expertise to filter by")
    
    results_type: Optional[Literal["پزشکان بیمارستانی", "پزشکان مطبی", "فقط پزشکان"]] = Field(
        None, description='Type of results to get ("پزشکان بیمارستانی", "پزشکان مطبی", "فقط پزشکان")'
    )
    
    doctor_gender: Optional[Literal["male", "female"]] = Field(None, description='Doctor gender ("male", "female")')
    
    degree: Optional[
        Literal["فلوشیپ", "فوق تخصص", "دکترای تخصصی", "متخصص", "دکترای", "کارشناس ارشد", "کارشناس"]
    ] = Field(None, description="Doctor's degree to filter by")
    
    turn_type: Optional[Literal["non-consult", "consult"]] = Field(None, description='Type of appointment ("non-consult", "consult")')
    
    good_behave_doctor: Optional[bool] = Field(None, description="Filter by good-behaving doctors")
    popular_doctor: Optional[bool] = Field(None, description="Filter by popular doctors")
    less_waiting_time_doctor: Optional[bool] = Field(None, description="Filter by doctors with less waiting time")
    has_prescription: Optional[bool] = Field(None, description="Filter by doctors who can give prescriptions")
    
    work_time_frames: Optional[List[Literal["night", "afternoon", "morning"]]] = Field(
        None, description="Time frames the doctor works (night, afternoon, morning)"
    )

@tool("find_doctor_tool", args_schema=FindDoctorInputSchema)
def find_doctor(text=None, 
                    city=None, 
                    expertise=None, 
                    sub_expertise=None, 
                    results_type=None, 
                    doctor_gender=None, 
                    degree=None, 
                    turn_type=None, 
                    good_behave_doctor=None, 
                    popular_doctor=None,
                    less_waiting_time_doctor=None,
                    has_prescription=None,
                    work_time_frames=None):
    
    return get_doctor_list(text,
                           city,
                           expertise,
                           sub_expertise,
                           results_type,
                           doctor_gender,
                           degree,
                           turn_type,
                           good_behave_doctor,
                           popular_doctor,
                           less_waiting_time_doctor,
                           has_prescription,
                           work_time_frames)



llm_model = ChatOpenAI(model_name="google/gemini-2.5-flash-preview-05-20", openai_api_base=LLM_BASE_URL, openai_api_key=OPENROUTER_API_KEY, temperature=0)


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
    ORTHOPEDICS = "orthopedics"
    OBSTETRICS_GYNECOLOGY = "obstetrics-gynecology"
    OPHTHALMOLOGY = "ophthalmology"
    GASTROENTEROLOGY = "gastroenterology"
    UROLOGY = "urology"
    ENDOCRINOLOGY = "endocrinology"
    CARDIOVASCULAR = "cardiovascular"
    INTERNAL = "internal"
    DENTAL_ORAL = "dental-oral"
    DERMATOLOGY = "dermatology"
    SURGERY = "surgery"
    PEDIATRICS = "pediatrics"
    PSYCHIATRY = "psychiatry"
    PULMONOLOGY = "pulmonology"
    OTORHINOLARYNGOLOGY = "otorhinolaryngology"
    GENERAL_PRACTITIONER = "general-practitioner"
    CORONA_VIRUS = "corona-virus"
    REHABILITATION = "rehabilitation"
    ANESTHESIA_AND_INTENSIVE_CARE = "anesthesia-and-intensive-care"
    NUTRITION = "nutrition"
    NEUROLOGY = "neurology"
    PSYCHOLOGY = "psychology"
    PALLIATIVE_CARE = "palliative-care"
    INFECTIOUS = "infectious"
    BEAUTY = "beauty"
    ONCOLOGY = "oncology"
    IMAGING = "imaging"
    DIABETES = "diabetes"
    PHARMACOLOGY = "pharmacology"
    TRADITIONAL_MEDICINE = "traditional-medicine"
    GENETICS = "genetics"
    ALLERGIES = "allergies"
    LABORATORY_AND_IMAGING = "laboratory-and-imaging"
    EMERGENCY_MEDICINE = "emergency-medicine"
    SEXUAL_HEALTH = "sexual-health"

class DiagnoseOutputClass(BaseModel):
    is_data_enough_for_initiall_diagnosis : bool = Field(..., description="")
    possible_diseases: list[str] = Field(..., description = "list of possible diseases")
    expertise: Optional[Literal["orthopedics", "obstetrics-gynecology", "ophthalmology", "gastroenterology", "urology", "endocrinology", "cardiovascular", "internal", "dental-oral", "dermatology", "surgery", "pediatrics", "psychiatry", "pulmonology", "otorhinolaryngology", "general-practitioner", "corona-virus", "rehabilitation", "anesthesia-and-intensive-care", "nutrition", "neurology", "psychology", "palliative-care", "infectious", "beauty", "oncology", "imaging", "diabetes", "pharmacology", "traditional-medicine", "genetics", "allergies", "laboratory-and-imaging", "emergency-medicine", "sexual-health"]] = Field(None, description='which expert is the best to refer to')


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
