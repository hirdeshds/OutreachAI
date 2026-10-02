import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from config.settings import FILTERED_DATA_PATH
from config.criteria import (
    MIN_FOLLOWERS,
    MAX_FOLLOWERS,
    MIN_ENGAGEMENT_RATE,
    TARGET_NICHE,
    BRAND_FIT_KEYWORDS,
    DISQUALIFIED_KEYWORDS
)

def calculate_brand_fit_score(influencer: Dict[str, Any]) -> int:
    text_corpus = (
        influencer.get("bio", "") + " " +
        " ".join(influencer.get("content_themes", [])) + " " +
        influencer.get("recent_post_summary", "")
    ).lower()
    
    matched_keywords = [kw for kw in BRAND_FIT_KEYWORDS if kw in text_corpus]
    raw_score = 50 + (len(matched_keywords) * 10)
    return min(100, raw_score)

def evaluate_influencer(influencer: Dict[str, Any]) -> Tuple[str, str, int]:
    followers = influencer.get("follower_count", 0)
    engagement = influencer.get("engagement_rate", 0.0)
    category = influencer.get("category", "")
    bio = influencer.get("bio", "").lower()
    
    for disq in DISQUALIFIED_KEYWORDS:
        if disq in bio:
            return "FAILED", f"Disqualified: Bio matches flagged keyword '{disq}'", 15

    if category != TARGET_NICHE:
        return "FAILED", f"Disqualified: Category '{category}' does not match target niche '{TARGET_NICHE}'", 20

    if followers < MIN_FOLLOWERS:
        return "FAILED", f"Disqualified: Follower count ({followers:,}) is below micro-influencer minimum ({MIN_FOLLOWERS:,})", 30

    if followers > MAX_FOLLOWERS:
        return "FAILED", f"Disqualified: Follower count ({followers:,}) exceeds micro-influencer threshold ({MAX_FOLLOWERS:,})", 45

    if engagement < MIN_ENGAGEMENT_RATE:
        return "FAILED", f"Disqualified: Engagement rate ({engagement}%) is below minimum threshold ({MIN_ENGAGEMENT_RATE}%)", 40

    fit_score = calculate_brand_fit_score(influencer)
    
    reason = (
        f"Passed: Valid micro-influencer ({followers:,} followers, {engagement}% engagement) "
        f"in {TARGET_NICHE} with {fit_score}/100 brand alignment."
    )
    return "PASSED", reason, fit_score

def filter_influencers(influencers: List[Dict[str, Any]]) -> Dict[str, Any]:
    passed_list = []
    failed_list = []
    all_evaluated = []

    for item in influencers:
        record = dict(item)
        status, reason, fit_score = evaluate_influencer(record)
        record["status"] = status
        record["filter_reason"] = reason
        record["brand_fit_score"] = fit_score
        
        all_evaluated.append(record)
        if status == "PASSED":
            passed_list.append(record)
        else:
            failed_list.append(record)

    summary = {
        "total_discovered": len(influencers),
        "total_passed": len(passed_list),
        "total_failed": len(failed_list),
        "pass_rate_pct": round((len(passed_list) / len(influencers)) * 100, 1) if influencers else 0.0
    }

    return {
        "summary": summary,
        "all": all_evaluated,
        "passed": passed_list,
        "failed": failed_list
    }

def save_filtered_influencers(filtered_data: Dict[str, Any], filepath: Path = FILTERED_DATA_PATH) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    return filepath
