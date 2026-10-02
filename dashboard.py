import streamlit as st
import pandas as pd
import json
from pathlib import Path

from config.settings import (
    RAW_DATA_PATH,
    FILTERED_DATA_PATH,
    ENRICHED_DATA_PATH,
    MESSAGES_DATA_PATH,
    TRACKER_CSV_PATH,
    DATA_DIR
)
from main import run_pipeline

st.set_page_config(
    page_title="OutreachAI – Micro-Influencer Discovery & Outreach",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_json_file(file_path: Path):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def load_csv_file(file_path: Path):
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()

def render_sidebar():
    st.sidebar.title("✨ OutreachAI Studio")
    st.sidebar.caption("Automated Micro-Influencer Discovery & Outreach")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Campaign Configuration")
    st.sidebar.info("**Niche:** Fashion & Beauty\n\n**Audience Range:** 5,000 – 100,000\n\n**Min Engagement:** 2.0%\n\n**Email Word Target:** 60–90\n\n**DM Word Target:** 15–30")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚀 Re-Run Full Pipeline", use_container_width=True):
        with st.spinner("Executing Discovery -> Filtering -> Enrichment -> Personalization -> Sending..."):
            run_pipeline()
            st.sidebar.success("Pipeline executed successfully!")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("Built for EDXSO AI Engineer Intern Assignment")

def render_overview_metrics(filtered_data, enriched_data, messages_data, tracker_df):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_discovered = filtered_data["summary"]["total_discovered"] if filtered_data else 0
    passed_count = filtered_data["summary"]["total_passed"] if filtered_data else 0
    failed_count = filtered_data["summary"]["total_failed"] if filtered_data else 0
    enriched_count = len(enriched_data) if enriched_data else 0
    tracker_count = len(tracker_df) if not tracker_df.empty else 0

    col1.metric("Discovered Creators", total_discovered)
    col2.metric("Passed Filtering", passed_count, f"{filtered_data['summary']['pass_rate_pct']}%" if filtered_data else "")
    col3.metric("Failed / Disqualified", failed_count)
    col4.metric("AI Messages Ready", enriched_count)
    col5.metric("Outreach Log Entries", tracker_count)

def render_discovery_filtering_tab(filtered_data):
    st.header("1 & 2. Influencer Discovery, Filtering & Classification")
    st.write("Browse all discovered micro-influencers and review automated qualification decisions.")

    if not filtered_data:
        st.warning("No data found. Please run the pipeline from the sidebar.")
        return

    all_creators = filtered_data.get("all", [])
    df = pd.DataFrame(all_creators)

    col1, col2 = st.columns([1, 2])
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "PASSED", "FAILED"])
    with col2:
        platform_filter = st.selectbox("Filter by Platform", ["All", "Instagram", "TikTok", "YouTube"])

    filtered_df = df
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]
    if platform_filter != "All":
        filtered_df = filtered_df[filtered_df["platform"] == platform_filter]

    display_cols = [
        "name", "platform", "follower_count", "engagement_rate",
        "category", "status", "filter_reason", "email"
    ]
    st.dataframe(
        filtered_df[display_cols].rename(columns={
            "name": "Creator Name",
            "platform": "Platform",
            "follower_count": "Followers",
            "engagement_rate": "Engagement %",
            "category": "Niche",
            "status": "Filter Status",
            "filter_reason": "Decision Explanation",
            "email": "Contact Email"
        }),
        use_container_width=True,
        height=400
    )

    st.subheader("Disqualification Insights")
    failed_creators = [c for c in all_creators if c["status"] == "FAILED"]
    for c in failed_creators:
        st.error(f"**{c['name']}** ({c['platform']} | {c['category']} | {c['follower_count']:,} followers) — *{c['filter_reason']}*")

def render_enrichment_tab(enriched_data):
    st.header("3. Profile Enrichment")
    st.write("Examine enriched creator profiles with verified contact signals, audience demographics, and collaboration strategies.")

    if not enriched_data:
        st.warning("No enriched data found.")
        return

    selected_name = st.selectbox(
        "Select Shortlisted Influencer to Inspect",
        [c["name"] for c in enriched_data]
    )
    creator = next((c for c in enriched_data if c["name"] == selected_name), None)

    if creator:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"### {creator['name']}")
            st.markdown(f"**Platform:** {creator['platform']}")
            st.markdown(f"**Profile URL:** [{creator['profile_url']}]({creator['profile_url']})")
            st.markdown(f"**Follower Count:** {creator['follower_count']:,}")
            st.markdown(f"**Tier:** `{creator.get('creator_tier', 'Micro')}`")
        with c2:
            st.markdown("### Metrics & Contact")
            st.markdown(f"**Engagement Rate:** `{creator['engagement_rate']}%`")
            st.markdown(f"**Est. Active Reach:** `{creator.get('estimated_active_engagement', 0):,}`")
            email_color = "green" if creator["email"] != "Not Found" else "red"
            st.markdown(f"**Contact Email:** :{email_color}[`{creator['email']}`]")
            st.markdown(f"**Website / Linktree:** {creator.get('website', 'Not Found')}")
        with c3:
            st.markdown("### Audience Demographics")
            st.markdown(f"**Audience Age:** {creator.get('audience_age', 'Not Found')}")
            st.markdown(f"**Audience Gender:** {creator.get('audience_gender', 'Not Found')}")
            st.markdown(f"**Geography:** {creator.get('audience_geography', 'Not Found')}")
            st.markdown(f"**Recommended Collab:** `{creator.get('suggested_collaboration')}`")

        st.markdown("---")
        st.markdown(f"**Bio Snippet:** *\"{creator.get('bio', '')}\"*")
        st.markdown(f"**Content Themes:** {', '.join([f'`{t}`' for t in creator.get('content_themes', [])])}")
        st.markdown(f"**Recent Post Context:** *{creator.get('recent_post_summary', '')}*")

def render_personalization_tab(messages_data):
    st.header("4. AI Message Personalization")
    st.write("Review dynamically tailored collaboration pitches for each shortlisted influencer.")

    if not messages_data:
        st.warning("No messages generated yet.")
        return

    creator_names = [m["influencer_name"] for m in messages_data]
    selected_creator = st.selectbox("Select Creator", creator_names)
    msg = next((m for m in messages_data if m["influencer_name"] == selected_creator), None)

    if msg:
        col_email, col_dm = st.columns(2)
        
        with col_email:
            st.subheader("✉️ A. Email Collaboration Pitch")
            email_valid = 60 <= msg["email_word_count"] <= 90
            badge_color = "green" if email_valid else "orange"
            st.markdown(f"**Length:** :{badge_color}[**{msg['email_word_count']} words**] *(Target: 60–90 words)*")
            st.markdown(f"**Angle:** `{msg.get('collaboration_angle')}`")
            st.markdown(f"**Subject:** `{msg.get('email_subject')}`")
            st.text_area("Email Body", msg.get("email_body"), height=250)

        with col_dm:
            st.subheader("💬 B. Instagram DM")
            dm_valid = 15 <= msg["dm_word_count"] <= 30
            dm_badge_color = "green" if dm_valid else "orange"
            st.markdown(f"**Length:** :{dm_badge_color}[**{msg['dm_word_count']} words**] *(Target: 15–30 words)*")
            st.markdown(f"**Engine Used:** `{msg.get('engine_used')}`")
            st.text_area("DM Text (Ready to send)", msg.get("instagram_dm"), height=150)
            st.info("💡 **Compliance Safe:** Complies with platform guidelines by queuing messages for simulated or manual operator dispatch.")

def render_sending_tracker_tab(tracker_df):
    st.header("5 & 6. Sending Layer & Outreach Tracker")
    st.write("Monitor outreach dispatches, duplicate prevention, and real-time delivery logs.")

    if tracker_df.empty:
        st.info("No outreach logs recorded yet.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Outreach Attempts", len(tracker_df))
    sent_yes = len(tracker_df[tracker_df["Sent"] == "Yes"])
    c2.metric("Dispatched / Simulated", sent_yes)
    c3.metric("Skipped / Duplicate Prevented", len(tracker_df) - sent_yes)

    st.subheader("Outreach Activity Log (outreach_tracker.csv)")
    st.dataframe(tracker_df, use_container_width=True, height=450)

    csv_data = tracker_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Outreach Tracker CSV",
        data=csv_data,
        file_name="outreach_tracker.csv",
        mime="text/csv"
    )

def main():
    render_sidebar()

    filtered_data = load_json_file(FILTERED_DATA_PATH)
    enriched_data = load_json_file(ENRICHED_DATA_PATH)
    messages_data = load_json_file(MESSAGES_DATA_PATH)
    tracker_df = load_csv_file(TRACKER_CSV_PATH)

    st.title("Automated Micro-Influencer Outreach System")
    st.caption("AI-Powered Discovery, Qualification, Enrichment, Personalization, Sending & Tracking Pipeline")

    render_overview_metrics(filtered_data, enriched_data, messages_data, tracker_df)
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 1. Discovery & Filtering",
        "📊 2. Profile Enrichment",
        "✍️ 3. AI Personalization",
        "🚀 4. Sending & Tracker"
    ])

    with tab1:
        render_discovery_filtering_tab(filtered_data)
    with tab2:
        render_enrichment_tab(enriched_data)
    with tab3:
        render_personalization_tab(messages_data)
    with tab4:
        render_sending_tracker_tab(tracker_df)

if __name__ == "__main__":
    main()
