import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "discovered_influencers.json"
FILTERED_DATA_PATH = DATA_DIR / "processed" / "filtered_influencers.json"
ENRICHED_DATA_PATH = DATA_DIR / "processed" / "enriched_influencers.json"
MESSAGES_DATA_PATH = DATA_DIR / "outreach" / "personalized_messages.json"
TRACKER_CSV_PATH = DATA_DIR / "outreach" / "outreach_tracker.csv"
DB_PATH = DATA_DIR / "outreach_history.db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "GlowAura Partnerships")
BRAND_NAME = os.getenv("BRAND_NAME", "GlowAura Beauty")
DEFAULT_CAMPAIGN = os.getenv("CAMPAIGN_TYPE", "UGC content creation")
SEND_MODE = os.getenv("SEND_MODE", "simulation")
