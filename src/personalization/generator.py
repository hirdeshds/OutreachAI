import json
import re
import httpx
import cohere
from pathlib import Path
from typing import List, Dict, Any
from config.settings import (
    COHERE_API_KEY,
    BRAND_NAME,
    MESSAGES_DATA_PATH
)
from src.personalization.prompts import build_unified_outreach_prompt

_cohere_client = None
_cohere_rate_limited = False

def count_words(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))

def strip_emojis(text: str) -> str:
    clean = re.sub(r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u200d\ufe0f]', '', text)
    clean = re.sub(r'[:;=]-?[)D(\]pP]', '', clean)
    return clean.strip()

def trim_to_word_limit(text: str, max_words: int = 88) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    trimmed = " ".join(words[:max_words])
    last_punc = max(trimmed.rfind("."), trimmed.rfind("!"), trimmed.rfind("?"))
    if last_punc > int(len(trimmed) * 0.6):
        return trimmed[:last_punc + 1]
    return trimmed + "."

def normalize_email_length(email_text: str, brand_name: str) -> str:
    words_count = count_words(email_text)
    if words_count < 60:
        expansion = (
            f" We deeply value authentic creator storytelling, and we are confident your audience "
            f"will appreciate testing our gentle, clinical-grade formulations."
        )
        email_text = email_text.rstrip() + expansion
    return trim_to_word_limit(email_text, max_words=88)

def extract_json_object(raw_text: str) -> dict:
    clean = raw_text.strip()
    if "```json" in clean:
        clean = clean.split("```json")[1].split("```")[0].strip()
    elif "```" in clean:
        clean = clean.split("```")[1].split("```")[0].strip()
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(clean[start:end + 1])
        except Exception:
            pass
    return {}

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

def get_cohere_client():
    global _cohere_client
    if _cohere_client is None and COHERE_API_KEY:
        try:
            transport = httpx.HTTPTransport(retries=0)
            http_cli = httpx.Client(timeout=8.0, transport=transport)
            _cohere_client = cohere.ClientV2(api_key=COHERE_API_KEY, httpx_client=http_cli)
        except Exception:
            pass
    return _cohere_client

def call_cohere_llm(prompt: str) -> str:
    global _cohere_rate_limited
    if not COHERE_API_KEY or _cohere_rate_limited:
        return ""
    
    client = get_cohere_client()
    if not client:
        return ""

    try:
        response = client.chat(
            model="command-r-08-2024",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )
        if response.message and response.message.content:
            return response.message.content[0].text or ""
    except Exception as exc:
        err_msg = str(exc).lower()
        if "429" in err_msg or "rate limit" in err_msg or "too many requests" in err_msg or "trial" in err_msg:
            _cohere_rate_limited = True
    return ""

def generate_personalized_messages(influencer: Dict[str, Any]) -> Dict[str, Any]:
    brand = BRAND_NAME
    angle = influencer.get("suggested_collaboration", "UGC content creation")
    
    email_subject = ""
    email_body = ""
    dm_body = ""
    engine_used = "Dynamic Semantic Synthesizer"

    if COHERE_API_KEY and not _cohere_rate_limited:
        try:
            prompt = build_unified_outreach_prompt(influencer, brand, angle)
            raw = call_cohere_llm(prompt)
            data = extract_json_object(raw)
            if data and data.get("email_body") and data.get("instagram_dm"):
                email_subject = strip_emojis(data.get("subject", f"Partnership: {brand} x {influencer.get('name')}"))
                email_body = strip_emojis(normalize_email_length(data.get("email_body", ""), brand))
                dm_body = strip_emojis(trim_to_word_limit(data.get("instagram_dm", ""), max_words=24))
                engine_used = "Cohere Command R"
        except Exception:
            pass

    if not email_body or not dm_body:
        fallback = generate_dynamic_fallback_messages(influencer, brand, angle)
        email_subject = strip_emojis(fallback["email_subject"])
        email_body = strip_emojis(fallback["email_body"])
        dm_body = strip_emojis(fallback["instagram_dm"])
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
    total = len(influencer_list)
    for idx, influencer in enumerate(influencer_list, start=1):
        name = influencer.get("name", "Creator")
        record = generate_personalized_messages(influencer)
        engine = record.get("engine_used", "AI")
        print(f"  [{idx}/{total}] Personalized: {name} (via {engine})", flush=True)
        personalized_records.append(record)
    return personalized_records

def save_personalized_messages(data: List[Dict[str, Any]], filepath: Path = MESSAGES_DATA_PATH) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath
