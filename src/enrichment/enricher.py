import json
from pathlib import Path
from typing import List, Dict, Any
from config.settings import ENRICHED_DATA_PATH

def determine_creator_tier(followers: int) -> str:
    if followers < 25000:
        return "Early Micro (5k-25k)"
    elif followers < 50000:
        return "Mid Micro (25k-50k)"
    else:
        return "Senior Micro (50k-100k)"

def suggest_collaboration_angle(platform: str, themes: List[str]) -> str:
    themes_str = " ".join(themes).lower()
    if platform.lower() == "tiktok":
        return "UGC short-form video & product reaction"
    elif platform.lower() == "youtube":
        return "Dedicated long-form video review & tutorial"
    elif "skincare" in themes_str:
        return "30-day glow routine sponsorship & before/after"
    elif "wardrobe" in themes_str or "fashion" in themes_str:
        return "Styling haul & seasonal lookbook integration"
    else:
        return "Brand ambassador & affiliate collaboration"

def enrich_single_profile(influencer: Dict[str, Any]) -> Dict[str, Any]:
    profile = dict(influencer)
    
    email = profile.get("email", "").strip()
    if not email or "@" not in email:
        profile["email"] = "Not Found"
        profile["has_valid_email"] = False
        profile["enrichment_status"] = "PARTIAL_NO_EMAIL"
    else:
        profile["has_valid_email"] = True
        profile["enrichment_status"] = "COMPLETE"

    followers = profile.get("follower_count", 0)
    engagement = profile.get("engagement_rate", 0.0)
    
    profile["creator_tier"] = determine_creator_tier(followers)
    profile["estimated_active_engagement"] = int(followers * (engagement / 100.0))
    profile["suggested_collaboration"] = suggest_collaboration_angle(
        profile.get("platform", "Instagram"),
        profile.get("content_themes", [])
    )
    
    if not profile.get("website"):
        profile["website"] = "Not Found"
    if not profile.get("audience_age"):
        profile["audience_age"] = "Not Found"
    if not profile.get("audience_gender"):
        profile["audience_gender"] = "Not Found"
    if not profile.get("audience_geography"):
        profile["audience_geography"] = "Not Found"

    return profile

def enrich_influencers(influencer_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched_results = []
    for item in influencer_list:
        enriched_record = enrich_single_profile(item)
        enriched_results.append(enriched_record)
    return enriched_results

def save_enriched_influencers(data: List[Dict[str, Any]], filepath: Path = ENRICHED_DATA_PATH) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath
