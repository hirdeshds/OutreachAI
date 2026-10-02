import json
import requests
from typing import List, Dict, Any

def fetch_creators_from_api(niche: str = "fashion-beauty") -> List[Dict[str, Any]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    sample_endpoint = f"https://collabstr.com/api/creators?category={niche}"
    try:
        response = requests.get(sample_endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def parse_creator_profile(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": raw_profile.get("name", "Unknown Creator"),
        "platform": raw_profile.get("platform", "Instagram"),
        "profile_url": raw_profile.get("profile_url", ""),
        "follower_count": int(raw_profile.get("follower_count", 0)),
        "engagement_rate": float(raw_profile.get("engagement_rate", 0.0)),
        "category": raw_profile.get("category", "General"),
        "content_themes": raw_profile.get("content_themes", []),
        "recent_post_summary": raw_profile.get("recent_post_summary", ""),
        "email": raw_profile.get("email", "Not Found"),
        "website": raw_profile.get("website", "Not Found"),
        "audience_age": raw_profile.get("audience_age", "Not Found"),
        "audience_gender": raw_profile.get("audience_gender", "Not Found"),
        "audience_geography": raw_profile.get("audience_geography", "Not Found"),
        "bio": raw_profile.get("bio", "")
    }
