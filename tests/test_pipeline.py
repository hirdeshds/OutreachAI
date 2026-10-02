import pytest
from src.discovery.discover import get_initial_influencers
from src.filtering.classifier import filter_influencers, evaluate_influencer
from src.enrichment.enricher import enrich_influencers, enrich_single_profile
from src.personalization.generator import generate_personalized_messages, count_words
from src.sending.email_sender import can_send_email, validate_email_address

def test_discovery_creator_count():
    creators = get_initial_influencers()
    assert len(creators) >= 50, f"Expected at least 50 creators, got {len(creators)}"

def test_filtering_logic():
    pass_creator = {
        "name": "Test Good",
        "follower_count": 25000,
        "engagement_rate": 3.5,
        "category": "Fashion & Beauty",
        "bio": "Skincare and beauty creator",
        "content_themes": ["Skincare"],
        "recent_post_summary": "Routine demo"
    }
    status, reason, score = evaluate_influencer(pass_creator)
    assert status == "PASSED"
    assert score >= 50

    fail_crypto = dict(pass_creator, category="Crypto & Web3")
    status_crypto, reason_crypto, _ = evaluate_influencer(fail_crypto)
    assert status_crypto == "FAILED"
    assert "target niche" in reason_crypto

    fail_macro = dict(pass_creator, follower_count=250000)
    status_macro, reason_macro, _ = evaluate_influencer(fail_macro)
    assert status_macro == "FAILED"
    assert "exceeds micro-influencer threshold" in reason_macro

    fail_low_engagement = dict(pass_creator, engagement_rate=0.5)
    status_eng, reason_eng, _ = evaluate_influencer(fail_low_engagement)
    assert status_eng == "FAILED"
    assert "below minimum threshold" in reason_eng

def test_enrichment_not_found_handling():
    no_email_creator = {
        "name": "Jane Doe",
        "platform": "Instagram",
        "profile_url": "https://instagram.com/janedoe",
        "follower_count": 12000,
        "engagement_rate": 3.2,
        "category": "Fashion & Beauty",
        "content_themes": ["Makeup"],
        "email": ""
    }
    enriched = enrich_single_profile(no_email_creator)
    assert enriched["email"] == "Not Found"
    assert enriched["has_valid_email"] is False
    assert enriched["enrichment_status"] == "PARTIAL_NO_EMAIL"

def test_message_word_counts():
    creator = {
        "name": "Maya Lin",
        "platform": "Instagram",
        "recent_post_summary": "Morning glass skin routine breaking down gentle hyaluronic acid layering and reef-safe SPF reviews.",
        "content_themes": ["Glass Skin Routines", "Korean Skincare"],
        "suggested_collaboration": "UGC content creation",
        "follower_count": 28000,
        "engagement_rate": 4.2
    }
    msgs = generate_personalized_messages(creator)
    email_words = msgs["email_word_count"]
    dm_words = msgs["dm_word_count"]
    
    assert 60 <= email_words <= 90, f"Email word count {email_words} is outside [60, 90]"
    assert 15 <= dm_words <= 30, f"DM word count {dm_words} is outside [15, 30]"

def test_duplicate_prevention():
    sent_history = {"already_contacted@example.com"}
    can_send, reason = can_send_email("already_contacted@example.com", sent_history)
    assert can_send is False
    assert "Duplicate prevented" in reason

    can_send_new, _ = can_send_email("new_partner@example.com", sent_history)
    assert can_send_new is True

    can_send_invalid, reason_inv = can_send_email("Not Found", sent_history)
    assert can_send_invalid is False
