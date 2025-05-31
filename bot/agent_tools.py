import time
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId
import os
import asyncio
from typing import Literal, Annotated
from pydantic import BaseModel, Field
from langchain.tools import tool
from typing import Literal, List
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, RemoveMessage, ToolMessage, HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import InjectedState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

from paziresh24_interface.paziresh24_utils import get_doctor_list, get_doctor_details, async_get_doctor_details

load_dotenv()


LLM_BASE_URL = os.getenv("LLM_BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
llm_model = ChatOpenAI(model_name="google/gemini-2.5-flash-preview-05-20", openai_api_base=LLM_BASE_URL, openai_api_key=OPENROUTER_API_KEY, temperature=0.2)


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
    
    step1_list = get_doctor_list(text,
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
    print(f"Step 1 list: {len(step1_list)}")
    filtered_list = [item for item in step1_list if item.get("url", "")][:5]
    
    tasks = []
    for doctor in filtered_list:
        tasks.append(async_get_doctor_details(doctor["url"]))
    # full_details_list = asyncio.run(asyncio.gather(*tasks))

    # full_details_list = []
    # for doctor in filtered_list:
    #     full_details_list.append(get_doctor_details(doctor["url"]))
    # full_details_list = [item for item in full_details_list if item]
    try:
        loop = asyncio.get_running_loop()
        asyncio.set_event_loop(loop)
        full_details_list = loop.run_until_complete(asyncio.gather(*tasks))
    except Exception as e:
        full_details_list = asyncio.run(asyncio.gather(*tasks))
    
    print(f"Full details list: {len(full_details_list)}")

    for i, doctor in enumerate(filtered_list):
        doctor["biography_text"] = full_details_list[i]["doctor"]["biography_text"]
    print(f"Filtered list: {len(filtered_list)}")
    
    # feedbacks_summaries = []
    # for doctor in full_details_list:
    #     feedbacks_summaries.append(
    #         llm_model.invoke(
    #             [
    #                 SystemMessage(content="You are a critical thinker and professional summarizer. summarize the feedbacks of the doctor into a single paragraph."),
    #                 HumanMessage(content="\n".join([f"{index}: {feedback["description"]}" for index, feedback in enumerate(doctor["feedbacks"]["feedbacks"]["list"][:5], start=1)])),
    #             ]
    #         )
    #     )
    tasks = []
    for doctor in full_details_list:
        tasks.append(llm_model.ainvoke(
                [
                    SystemMessage(content="You are a critical thinker and professional summarizer. summarize the feedbacks of the doctor into a single persian paragraph."),
                    HumanMessage(content="\n".join([f"{index}: {feedback["description"]}" for index, feedback in enumerate(doctor["feedbacks"]["feedbacks"].get("list", [])[:5], start=1)])),
                ]
            ))
    feedbacks_summaries = asyncio.run(asyncio.gather(*tasks))
    # try:
    #     feedbacks_summaries = asyncio.run(asyncio.gather(*tasks))
    # except Exception as e:
    #     loop = asyncio.get_running_loop()
    #     asyncio.set_event_loop(loop)
    #     feedbacks_summaries = loop.run_until_complete(asyncio.gather(*tasks))
        
    # add the summarized feedbacks to each doctor in the filtered list
    print(f"Feedbacks summaries: {len(feedbacks_summaries)}")
    for i, doctor in enumerate(filtered_list):
        doctor["feedbacks_summary"] = feedbacks_summaries[i].content
    with open("filtered_list.json", "w", encoding="utf-8") as f:
        import json
        json.dump(filtered_list, f, ensure_ascii=False, indent=4)
    return filtered_list






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



# ⬇️  NEW schema + tool


@tool("update_long_term_profile")
def update_long_term_profile(
    data: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Persist the given `data` to state['current_profile'] (one item per line).
    Call **only** when you learn a brand-new, reusable fact about the user.
    param: data: str - the new data to add to the profile
    """
    profile: str = state.get("current_profile", "").strip()
    if data in profile.splitlines():
        confirmation = "ℹ️ این اطلاعات از قبل در پروفایل وجود داشت."
    else:
        profile = f"{profile}\n- {data}" if profile else f"- {data}"
        confirmation = "✅ پروفایل کاربر به‌روز شد."
    return Command(update={
        "current_profile": profile,
        "messages": [ToolMessage(confirmation, tool_call_id=tool_call_id)]
    })
    
    
# ─────────────────────────────────────────────────────────────────────────────
# 📅  ONE shared mock schedule for every doctor (Khordad 1404)
# ─────────────────────────────────────────────────────────────────────────────
import locale, jdatetime
from datetime import timedelta
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from typing import Annotated, List

locale.setlocale(locale.LC_ALL, jdatetime.FA_LOCALE)

# Same slots for *all* doctors
SHARED_SLOTS: List[jdatetime.datetime] = sorted([
    jdatetime.datetime(1404, 3, 8,  9,  0),
    jdatetime.datetime(1404, 3, 9, 10,  0),
    jdatetime.datetime(1404, 3,10, 11,  0),
    jdatetime.datetime(1404, 3,11, 15,  0),
    jdatetime.datetime(1404, 3,12,  9,  0),
    jdatetime.datetime(1404, 3,13, 10, 30),
    jdatetime.datetime(1404, 3,14, 17,  0),
    jdatetime.datetime(1404, 3,15, 14,  0),
    jdatetime.datetime(1404, 3,16, 13,  0),
    jdatetime.datetime(1404, 3,17,  9, 30),
    jdatetime.datetime(1404, 3,18, 10,  0),
    jdatetime.datetime(1404, 3,18, 16,  0),
])

# ─────────────────────────────────────────────────────────────────────────────
# 🛠️  Tool 1 – doctor_available_times
# ─────────────────────────────────────────────────────────────────────────────
class DoctorAvailableTimesSchema(BaseModel):
    """دریافت بازه‌های خالی یک پزشک در یک هفته قبل و بعد از زمان دلخواه کاربر"""
    doctor_name: str = Field(..., description="نام پزشک (برای نمایش پیغام)")
    preferred_time: str = Field(
        ...,
        description="تاریخ و ساعت مدنظر به صورت جلالی «YYYY-MM-DD HH:MM» یا فقط «YYYY-MM-DD»",
    )

@tool("doctor_available_times", args_schema=DoctorAvailableTimesSchema)
def doctor_available_times(doctor_name: str, preferred_time: str) -> str:
    # Parse preferred_time
    preferred_time = preferred_time.strip()
    try:
        pref_dt = (jdatetime.datetime.strptime(preferred_time, "%Y-%m-%d %H:%M")
                   if " " in preferred_time
                   else jdatetime.datetime.strptime(preferred_time, "%Y-%m-%d"))
    except ValueError:
        return "❌ فرمت تاریخ/ساعت نامعتبر است. مثال: «1404-03-10 10:00»"

    # Window ±7 days
    start, end = pref_dt - timedelta(days=7), pref_dt + timedelta(days=7)
    window_slots = [s for s in SHARED_SLOTS if start <= s <= end]

    if not window_slots:
        return "⛔ در این بازه زمانی، نوبت خالی وجود ندارد."

    return "\n".join(s.strftime("%A %Y/%m/%d ساعت %H:%M") for s in window_slots)

# ─────────────────────────────────────────────────────────────────────────────
# 🛠️  Tool 2 – reserve_appointment
# ─────────────────────────────────────────────────────────────────────────────
class ReserveAppointmentSchema(BaseModel):
    """رزرو نوبت برای زمان مشخص"""
    doctor_name: str = Field(..., description="نام پزشک (صرفاً برای پیام تأیید)")
    desired_time: str = Field(..., description="«YYYY-MM-DD HH:MM» به تقویم جلالی")

@tool("reserve_appointment", args_schema=ReserveAppointmentSchema)
def reserve_appointment(doctor_name: str, desired_time: str) -> str:
    """Reserve an appointment for the given doctor at the specified Jalali date and time."""
    desired_time = desired_time.strip()
    try:
        desired_dt = jdatetime.datetime.strptime(desired_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return "❌ فرمت تاریخ/ساعت نامعتبر است."

    # Exact match → reserve
    if desired_dt in SHARED_SLOTS:
        SHARED_SLOTS.remove(desired_dt)
        msg = f"✅ نوبت شما با «{doctor_name}» رزرو شد:\n" + desired_dt.strftime("%A %Y/%m/%d ساعت %H:%M")
        return msg

    # Suggest closest before / after
    before = max([s for s in SHARED_SLOTS if s < desired_dt], default=None)
    after  = min([s for s in SHARED_SLOTS if s > desired_dt], default=None)
    suggestions = "⛔ این زمان پر است.\n"
    if before:
        suggestions += "• قبل: " + before.strftime("%A %Y/%m/%d ساعت %H:%M") + "\n"
    if after:
        suggestions += "• بعد:  " + after.strftime("%A %Y/%m/%d ساعت %H:%M")
    return suggestions

