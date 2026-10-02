from typing import List, Dict, Any

def prepare_dm_queue(personalized_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    dm_queue = []
    for msg in personalized_messages:
        dm_item = {
            "influencer": msg.get("influencer_name"),
            "platform": msg.get("platform"),
            "profile_url": msg.get("profile_url"),
            "dm_text": msg.get("instagram_dm"),
            "dm_word_count": msg.get("dm_word_count"),
            "workflow_type": "Manual / Simulated DM Dispatch",
            "compliance_note": "Compliant with Meta API terms (avoids scraping/unauthorized automation)",
            "status": "READY_FOR_COPY"
        }
        dm_queue.append(dm_item)
    return dm_queue

def dispatch_simulated_dm(dm_item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "influencer": dm_item.get("influencer"),
        "platform": dm_item.get("platform"),
        "channel": "Instagram/TikTok DM",
        "sent": "Yes",
        "status": "DISPATCHED_SIMULATED",
        "detail": f"Queued for operator copy-paste to {dm_item.get('profile_url')}"
    }
