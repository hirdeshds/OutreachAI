def build_email_prompt(influencer: dict, brand_name: str, collaboration_angle: str) -> str:
    return f"""You are a senior brand partnerships manager for {brand_name}.
Write a highly personalized collaboration pitch email for an influencer.

Rules:
1. Length: Exactly between 60 and 90 words.
2. Must mention their name ({influencer.get('name')}).
3. Reference their recent content: "{influencer.get('recent_post_summary')}".
4. Align with their content themes: {', '.join(influencer.get('content_themes', []))}.
5. Propose this collaboration angle: {collaboration_angle}.
6. Highlight mutual value: gifting full product range + competitive creator compensation.
7. Tone: warm, respectful, authentic, never spammy.
8. Output JSON only in this exact format:
{{"subject": "Short compelling subject line", "body": "Email body text (60-90 words)"}}"""

def build_dm_prompt(influencer: dict, brand_name: str, collaboration_angle: str) -> str:
    return f"""You are reaching out to an influencer via Instagram/TikTok DM for {brand_name}.

Rules:
1. Length: Exactly between 15 and 30 words.
2. Conversational, punchy, friendly, natural.
3. Mention their name ({influencer.get('name')}) and reference their recent style/content: "{influencer.get('recent_post_summary')[:60]}...".
4. Propose a quick chat regarding a {collaboration_angle}.
5. Output plain text DM only, no quotes, no extra remarks."""
