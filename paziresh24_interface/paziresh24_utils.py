import json
import requests
import aiohttp
from bs4 import BeautifulSoup

def retry_request(url, max_retry=3):
    while max_retry > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            else:
                print(f"Request failed with status code {response.status_code}. Retrying...")
        except requests.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
        max_retry -= 1

def get_doctor_details(url):
    if url.startswith('/dr/'):
        url = f"https://www.paziresh24.com{url}"
    

    response = retry_request(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    
    script_tag = soup.find('script', id='__NEXT_DATA__')
    if script_tag:
        script_content = script_tag.string
        data = json.loads(script_content)
        data = simplify_single_doctor_data(data)
    else:
        data = {}
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
                data = simplify_single_doctor_data(data)
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
                online_visit_url = "https://www.paziresh24.com" + action.get("url")
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
            "online_visit_url": online_visit_url,
            "url": doctor.get("url", ""),
            "id": doctor.get("id", "")
        })

    return simplified_doctors
    


def simplify_single_doctor_data(raw: dict) -> dict:
    """
    Extract the key information a consumer app or page would normally show
    from the full doctor‑profile payload that comes from the پذیرش۲۴ API.

    Parameters
    ----------
    raw : dict
        The full JSON object (what you pasted—`{"props": {"pageProps": …}}`).

    Returns
    -------
    dict
        A slimmed‑down dictionary containing:
        • title, description  
        • doctor (core personal & professional data)  
        • centers (each clinic/moffice with essential contact & schedule data)  
        • feedbacks (if the API included them)
    """
    # ---- helpers ----------------------------------------------------------
    def _prune_expertise(item: dict) -> dict:
        """Return only human‑readable parts of an expertise entry."""
        return {
            "degree": item.get("academic_degree", {}).get("title"),
            "speciality": item.get("speciality", {}).get("title"),
            "alias": item.get("alias"),
        }

    def _prune_service(svc: dict) -> dict:
        """Return the bits a patient actually sees when booking."""
        hours = svc.get("hours_of_work") or []
        return {
            "id": svc.get("id"),
            "title": svc.get("alias_title"),
            "price": svc.get("free_price"),
            "duration": svc.get("duration"),
            "hours_of_work": [
                {
                    "day": hw.get("day"),
                    "from": hw.get("from"),
                    "to": hw.get("to"),
                }
                for hw in hours
            ],
        }

    def _prune_center(center: dict) -> dict:
        """Keep the public‑facing parts of a clinic/office record."""
        services = center.get("services") or []
        return {
            "id": center.get("id"),
            "name": center.get("name"),
            "address": center.get("address"),
            "city": center.get("city"),
            "province": center.get("province"),
            "phone": center.get("display_number"),
            "map": center.get("map"),  # includes lat / lon
            "services": [_prune_service(s) for s in services],
        }

    # ---- main -------------------------------------------------------------
    page = raw.get("props", {}).get("pageProps", {})

    info = page.get("information", {})
    doctor = {
        "id": info.get("id"),
        "display_name": info.get("display_name"),
        "first_name": info.get("name"),
        "last_name": info.get("family"),
        "biography_html": info.get("biography"),
        "biography_text": biography_html_to_text(info.get("biography")),
        "experience_years": info.get("experience"),
        "gender": info.get("gender"),
        "avatar": info.get("image"),
        "city_slug": info.get("city_en_slug"),
        "expertises": [_prune_expertise(e) for e in info.get("expertises", [])],
    }

    slim = {
        "title": page.get("title"),
        "description": page.get("description"),
        "doctor": doctor,
        "centers": [_prune_center(c) for c in page.get("centers", [])],
    }

    # keep patient feedback / ratings if present
    if "feedbacks" in page:
        slim["feedbacks"] = page["feedbacks"]

    return slim

def biography_html_to_text(html: str) -> str:
    """
    Convert the raw HTML biography that comes from پذیرش۲۴ into plain text.

    • Replaces <p>, <br> and similar tags with new‑lines so the text keeps its
      paragraph structure.
    • Strips every other tag.
    • Unescapes HTML entities (&amp;, &nbsp;, …).
    • Collapses repeated whitespace.

    Parameters
    ----------
    html : str
        The `information["biography"]` field (may be None).

    Returns
    -------
    str
        A plain‑text version of the biography. Empty string if `html` is falsy.
    """
    if not html:
        return ""

    # ------------------------------------------------------------
    # 1️⃣  Preferred path – BeautifulSoup (cleaner handling)
    # ------------------------------------------------------------
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Replace <br> and block tags with newline hints before text extraction
        for br in soup.select("br"):
            br.replace_with("\n")
        for p in soup.select("p"):
            # Keep the text of <p> but ensure paragraph break afterwards
            p.append("\n")

        text = soup.get_text(separator=" ", strip=True)

    # ------------------------------------------------------------
    # 2️⃣  Fallback – regex + stdlib only
    # ------------------------------------------------------------
    except ModuleNotFoundError:
        import re
        from html import unescape

        # Normalize common block‑level breaks to \n
        html = re.sub(r"(?i)<\s*(br|/p)\s*/?>", "\n", html)
        # Drop all remaining tags
        text = re.sub(r"<[^>]+>", "", html)
        # HTML entities → characters
        text = unescape(text)

    # ------------------------------------------------------------
    # Final tidy‑up (shared)
    # ------------------------------------------------------------
    import re

    # Collapse multiple new‑lines & spaces, keep single line breaks
    text = re.sub(r"[ \t\r\f\v]+", " ", text)      # normalize spaces
    text = re.sub(r"\n{3,}", "\n\n", text)          # max 1 blank line
    text = text.strip()

    return text