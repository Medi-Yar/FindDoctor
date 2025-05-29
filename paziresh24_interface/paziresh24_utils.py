import json
import requests
import aiohttp
from bs4 import BeautifulSoup

def get_doctor_details(url):
    if url.startswith('/dr/'):
        url = f"https://www.paziresh24.com{url}"
        
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')


    script_tag = soup.find('script', id='__NEXT_DATA__')
    if script_tag:
        script_content = script_tag.string
        data = json.loads(script_content)
    return data

async def async_get_doctor_details(url):
    if url.startswith('/dr/'):
        url = f"https://www.paziresh24.com{url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')

            script_tag = soup.find('script', id='__NEXT_DATA__')
            if script_tag:
                script_content = script_tag.string
                data = json.loads(script_content)
                return data
    return None



def get_doctor_list(text=None, 
                    city="tehran", 
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
    """
    Get the list of doctors in a specific city.
    :param text: The search text (symptom, disease or expertise)
    :param city: The city to get the doctor list from.
    :param expertise: The expertise of doctors to filter by.
    :param sub_expertise: The sub-expertise of doctors to filter by.
    :param results_type: The type of results to get ("پزشکان بیمارستانی", "پزشکان مطبی", "فقط پزشکان")
    :param doctor_gender: The gender of doctors to filter by ("male", "female")
    :param degree: The degree of doctors to filter by ("فلوشیپ", "فوق تخصص", "دکترای تخصصی", "متخصص", "دکترای", "کارشناس ارشد", "کارشناس")
    :param turn_type: (non-consult, consult)
    :param good_behave_doctor: true if you want to filter by good behave doctors, false otherwise.
    :param popular_doctor: true if you want to filter by popular doctors, false otherwise.
    :param less_waiting_time_doctor: true if you want to filter by doctors with less waiting time, false otherwise.
    :param has_prescription: true if you want to filter by doctors who have prescription, false otherwise.
    :param work_time_frames: The work time frames of doctors to filter by. (night, afternoon, morning)


    """
    if expertise or sub_expertise:
        current_expertise = sub_expertise if sub_expertise else expertise
        url = f"https://www.paziresh24.com/s/{city}/{current_expertise}/"
    else:
        url = f"https://www.paziresh24.com/s/{city}/"
    
    # add the rest of the parameters as get query parameters
    

    params = {}
    if text:
        params['text'] = text
    if results_type:
        params['results_type'] = results_type
    if doctor_gender:
        params['doctor_gender'] = doctor_gender
    if degree:
        params['degree'] = degree
    if turn_type:
        params['turn_type'] = turn_type
    if good_behave_doctor is not None:
        params['good_behave_doctor'] = good_behave_doctor
    if popular_doctor is not None:
        params['popular_doctor'] = popular_doctor
    if less_waiting_time_doctor is not None:
        params['less_waiting_time_doctor'] = less_waiting_time_doctor
    if has_prescription is not None:
        params['has_prescription'] = has_prescription
    if work_time_frames:
        params['work_time_frames'] = work_time_frames
    
    response = requests.get(url, params=params)

    soup = BeautifulSoup(response.text, 'html.parser')


    script_tag = soup.find('script', id='__NEXT_DATA__')
    if script_tag:
        script_content = script_tag.string
        data = json.loads(script_content)
    data = data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}).get("queries", [{}])[0].get("state", {}).get("data", {}).get("search", {}).get("result", [])
    data = simplify_doctor_data(data)
    return data
    
def simplify_doctor_data(data):
    simplified_doctors = []

    for doctor in data:
        # Basic fields
        name = doctor.get("title", "")
        prefix = doctor.get("prefix", "")
        full_name = f"{prefix} {name}".strip()
        expertise = doctor.get("display_expertise", "")
        experience = doctor.get("experience", 0)
        satisfaction = doctor.get("satisfaction", 0)
        rating = doctor.get("rate_info", {}).get("rate", None)
        rates_count = doctor.get("rates_count", 0)
        visit_count = doctor.get("number_of_visits", 0)
        address = doctor.get("display_address", "")
        booking_available = doctor.get("consult_active_booking", False)

        # Online visit action (if available)
        actions = doctor.get("actions", [])
        online_visit_url = None
        appointment_time = None
        for action in actions:
            if "ویزیت آنلاین" in action.get("title", ""):
                online_visit_url = action.get("url")
            if "نوبت‌دهی" in action.get("title", ""):
                # Extract first appointment time if available
                top_title = action.get("top_title", "")
                if "اولین نوبت" in top_title:
                    appointment_time = top_title.replace("<span>", "").replace("</span>", "").strip()

        simplified_doctors.append({
            "full_name": full_name,
            "title": prefix,
            "expertise_summary": expertise,
            "experience_years": experience,
            "satisfaction_percent": satisfaction,
            "rating": rating,
            "number_of_ratings": rates_count,
            "visit_count": visit_count,
            "address": address,
            "online_booking_available": booking_available,
            "first_appointment_time": appointment_time,
            "online_visit_url": online_visit_url
        })

    return simplified_doctors
    