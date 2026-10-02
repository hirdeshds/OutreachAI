import json
import re
from pathlib import Path
from typing import List, Dict, Any
from config.settings import (
    COHERE_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    BRAND_NAME,
    MESSAGES_DATA_PATH
)
from src.personalization.prompts import build_email_prompt, build_dm_prompt

def count_words(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))

def generate_dynamic_fallback_messages(influencer: Dict[str, Any], brand_name: str, angle: str) -> Dict[str, Any]:
    name = influencer.get("name", "Creator").split()[0]
    recent = influencer.get("recent_post_summary", "")
    themes = influencer.get("content_themes", ["beauty"])
    main_theme = themes[0] if themes else "skincare"
    
    subject = f"Collaboration: {brand_name} x {name} – {angle.title()}"
    
    email_body = (
        f"Hi {name},\n\n"
        f"Loved your recent post on {recent.lower().rstrip('.')}. "
        f"Your focus on {main_theme.lower()} resonates deeply with our community.\n\n"
        f"At {brand_name}, we are launching a new {angle.lower()} campaign. "
        f"We would love to gift our complete skincare collection plus compensation for your authentic review. "
        f"Your audience is an ideal fit for this partnership.\n\n"
        f"Could we share the brief this week?\n\n"
        f"Best,\n"
        f"Partnerships Team at {brand_name}"
    )

    dm_body = (
        f"Hey {name}! Loved your recent post on {main_theme.lower()}. "
        f"Would you be open to a quick {angle.lower()} collab with {brand_name}?"
    )

    return {
        "email_subject": subject,
        "email_body": email_body,
        "instagram_dm": dm_body,
        "generation_engine": "Dynamic Semantic Synthesizer"
    }

def call_cohere_llm(prompt: str) -> str:
    if not COHERE_API_KEY:
        return ""
    try:
        import cohere
        client = cohere.ClientV2(api_key=COHERE_API_KEY)
        response = client.chat(
            model="command-r-plus-08-2024",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        if response.message and response.message.content:
            return response.message.content[0].text or ""
    except Exception:
        pass
    return ""

def call_groq_llm(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content or ""

def call_openai_llm(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400
    )
    return response.choices[0].message.content or ""

def generate_personalized_messages(influencer: Dict[str, Any]) -> Dict[str, Any]:
    brand = BRAND_NAME
    angle = influencer.get("suggested_collaboration", "UGC content creation")
    
    email_subject = ""
    email_body = ""
    dm_body = ""
    engine_used = "Dynamic Semantic Synthesizer"

    if COHERE_API_KEY:
        try:
            email_prompt = build_email_prompt(influencer, brand, angle)
            email_raw = call_cohere_llm(email_prompt)
            data = json.loads(email_raw[email_raw.find("{"):email_raw.rfind("}")+1])
            email_subject = data.get("subject", "")
            email_body = data.get("body", "")

            dm_prompt = build_dm_prompt(influencer, brand, angle)
            dm_body = call_cohere_llm(dm_prompt).strip('"')
            engine_used = "Cohere Command R+"
        except Exception:
            pass

    if not email_body and GROQ_API_KEY:
        try:
            email_prompt = build_email_prompt(influencer, brand, angle)
            email_raw = call_groq_llm(email_prompt)
            data = json.loads(email_raw[email_raw.find("{"):email_raw.rfind("}")+1])
            email_subject = data.get("subject", "")
            email_body = data.get("body", "")

            dm_prompt = build_dm_prompt(influencer, brand, angle)
            dm_body = call_groq_llm(dm_prompt).strip('"')
            engine_used = "Groq LLaMA 3.3"
        except Exception:
            pass

    if not email_body and OPENAI_API_KEY:
        try:
            email_prompt = build_email_prompt(influencer, brand, angle)
            email_raw = call_openai_llm(email_prompt)
            data = json.loads(email_raw[email_raw.find("{"):email_raw.rfind("}")+1])
            email_subject = data.get("subject", "")
            email_body = data.get("body", "")

            dm_prompt = build_dm_prompt(influencer, brand, angle)
            dm_body = call_openai_llm(dm_prompt).strip('"')
            engine_used = "OpenAI GPT-4o-mini"
        except Exception:
            pass

    if not email_body or not dm_body:
        fallback = generate_dynamic_fallback_messages(influencer, brand, angle)
        email_subject = fallback["email_subject"]
        email_body = fallback["email_body"]
        dm_body = fallback["instagram_dm"]
        engine_used = fallback["generation_engine"]

    return {
        "influencer_name": influencer.get("name"),
        "platform": influencer.get("platform"),
        "profile_url": influencer.get("profile_url"),
        "email": influencer.get("email"),
        "follower_count": influencer.get("follower_count"),
        "engagement_rate": influencer.get("engagement_rate"),
        "collaboration_angle": angle,
        "email_subject": email_subject,
        "email_body": email_body,
        "email_word_count": count_words(email_body),
        "instagram_dm": dm_body,
        "dm_word_count": count_words(dm_body),
        "engine_used": engine_used
    }

def personalize_all(influencer_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    personalized_records = []
    for influencer in influencer_list:
        record = generate_personalized_messages(influencer)
        personalized_records.append(record)
    return personalized_records

def save_personalized_messages(data: List[Dict[str, Any]], filepath: Path = MESSAGES_DATA_PATH) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath
