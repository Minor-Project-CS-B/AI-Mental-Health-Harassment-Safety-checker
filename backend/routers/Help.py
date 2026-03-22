from fastapi import APIRouter, Depends
from utils.security import get_current_user
from models.schemas import TokenData

router = APIRouter(prefix="/help", tags=["Help & Support"])

HELPLINES = {
    "emergency": [
        {"name": "Emergency Services",    "number": "112", "available": "24/7", "description": "Police, Ambulance, Fire — call if in immediate danger."},
        {"name": "Women Helpline",         "number": "181", "available": "24/7", "description": "National helpline for women in distress."},
        {"name": "Child Helpline",         "number": "1098","available": "24/7", "description": "For children and young people in crisis."},
    ],
    "mental_health": [
        {"name": "iCall – TISS",           "number": "9152987821",  "available": "Mon–Sat 8am–10pm", "description": "Free psychosocial support for students and professionals.", "url": "https://icallhelpline.org"},
        {"name": "Vandrevala Foundation",  "number": "1860-2662-345","available": "24/7",            "description": "Free mental health support helpline."},
        {"name": "NIMHANS",                "number": "080-46110007", "available": "Mon–Sat 8am–8pm", "description": "National Institute of Mental Health and Neurosciences."},
        {"name": "Snehi",                  "number": "044-24640050", "available": "24/7",            "description": "Suicide prevention and emotional support helpline."},
        {"name": "Aasra",                  "number": "9820466627",   "available": "24/7",            "description": "Helpline for people in emotional distress."},
    ],
    "harassment_safety": [
        {"name": "Cyber Crime Reporting",  "number": "1930",         "available": "24/7",            "description": "Report online harassment, cyberstalking, and fraud.", "url": "https://cybercrime.gov.in"},
        {"name": "Women in Distress",      "number": "1091",         "available": "24/7",            "description": "Women's safety helpline."},
        {"name": "National Commission for Women", "number": "7827170170", "available": "Mon–Sat 9am–5pm", "description": "Complaints related to harassment and discrimination.", "url": "https://ncw.nic.in"},
    ],
    "online_resources": [
        {"name": "iCall Online Counseling", "url": "https://icallhelpline.org",  "description": "Book a session with a professional counselor."},
        {"name": "Vandrevala Chat Support", "url": "https://www.vandrevalafoundation.com", "description": "Chat-based mental health support."},
        {"name": "Cyber Crime Portal",      "url": "https://cybercrime.gov.in",  "description": "File online complaint for cyber harassment."},
    ],
}


@router.get("/")
async def get_help_resources(current_user: TokenData = Depends(get_current_user)):
    """Returns all helpline numbers and support resources."""
    return {
        "disclaimer": (
            "These helplines are real, verified numbers available in India. "
            "In any emergency, always call 112 first."
        ),
        "resources": HELPLINES,
    }


@router.get("/emergency")
async def get_emergency_contacts(current_user: TokenData = Depends(get_current_user)):
    """Quick access — returns only emergency contacts."""
    return {"emergency_contacts": HELPLINES["emergency"]}