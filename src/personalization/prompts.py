def build_unified_outreach_prompt(influencer: dict, brand_name: str, collaboration_angle: str) -> str:
    name = influencer.get("name", "Creator")
    recent = influencer.get("recent_post_summary", "")
    themes = ", ".join(influencer.get("content_themes", []))

    return f"""You are a brand partnerships director for {brand_name}.
Generate 2 outreach messages for this micro-influencer:
- Name: {name}
- Recent Content: "{recent}"
- Content Themes: {themes}
- Collaboration Angle: {collaboration_angle}

MANDATORY RULES:
1. "subject": Catchy, professional subject line (under 10 words).
2. "email_body": Personalized pitch email. Length MUST BE between 65 and 85 words (STRICT REQUIREMENT: must be at least 60 words and at most 90 words). Paragraph 1: appreciate their specific recent content. Paragraph 2: introduce the {collaboration_angle} campaign and offer full product range gifting plus paid creator compensation. Paragraph 3: ask if they are open to reviewing the campaign brief this week.
3. "instagram_dm": Punchy, conversational DM. Length MUST BE between 18 and 26 words (STRICT: 15-30 words).
4. EMOJI BAN: Do NOT include any emojis or emoticons under any circumstances. Use plain text only.

Return ONLY valid JSON in this exact structure:
{{
  "subject": "...",
  "email_body": "...",
  "instagram_dm": "..."
}}"""
