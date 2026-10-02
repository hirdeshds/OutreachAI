# Automated Micro-Influencer Outreach System

An end-to-end automated system that discovers relevant micro-influencers, filters and classifies them based on strict criteria, enriches creator profiles with verified contact metrics, and generates highly personalized collaboration outreach messages (Email pitch and Instagram DM) with duplicate-safe delivery tracking.

Built for the **EDXSO AI Engineer Intern Assignment**.

---

## Architecture Overview

```
                      [ Public Creator Directories / UGC Marketplaces ]
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. DISCOVERY LAYER (src/discovery/discover.py)                                          │
│    • Fetches 50+ micro-influencer profiles across Instagram, TikTok, and YouTube       │
│    • Captures handles, metrics, niche categories, bios, and public business contacts   │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. FILTERING & CLASSIFICATION (src/filtering/classifier.py)                            │
│    • Category Check: Target Niche ("Fashion & Beauty")                                 │
│    • Follower Range: 5,000 to 100,000 (Micro-Influencer threshold)                     │
│    • Engagement Rate: Minimum 2.0%                                                     │
│    • Brand Fit & Spam Keyword Analysis (0–100 score)                                   │
│    • Outputs explicit "PASSED" or "FAILED" status with clear reasoning                │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. PROFILE ENRICHMENT (src/enrichment/enricher.py)                                     │
│    • Validates mandatory fields (Name, Platform, URL, Followers, Engagement, Niche)    │
│    • Verifies contact email (marks "Not Found" if unavailable – no fabricated emails)   │
│    • Enriches with Audience Demographics (Age, Gender, Geography)                      │
│    • Assigns creator tiers and optimal collaboration angles (UGC, Review, Sponsorship) │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. AI PERSONALIZATION LAYER (src/personalization/generator.py)                          │
│    • Dual Outreach Generation:                                                         │
│      A. Email Pitch: Exactly 60–90 words, references recent post & collaboration angle  │
│      B. Instagram DM: Exactly 15–30 words, punchy, conversational, and direct          │
│    • Multi-engine support: OpenAI GPT-4o-mini / Groq LLaMA 3.3 / Dynamic AI Synthesizer│
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. SENDING & SIMULATION LAYER (src/sending/email_sender.py & dm_manager.py)            │
│    • Email Dispatch: Real SMTP (Gmail/Custom) or zero-credential Sandbox Simulation   │
│    • Duplicate Prevention: Pre-flight check against historical outreach database       │
│    • Instagram DM Dispatch: Safe queue for operator dispatch (Meta TOS compliant)      │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. OUTREACH TRACKER & PERSISTENCE (src/tracking/tracker.py)                            │
│    • SQLite Database (`data/outreach_history.db`) for ACID storage & deduplication     │
│    • Live CSV Tracker (`data/outreach/outreach_tracker.csv`) for reporting             │
│    • Interactive Streamlit Dashboard (`dashboard.py`) for visual inspection           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
OutreachAI/
│
├── config/
│   ├── settings.py              # Central environment variables, paths, and defaults
│   └── criteria.py              # Follower bounds, engagement threshold, and niche keywords
│
├── src/
│   ├── discovery/
│   │   ├── scraper.py           # Creator profile parser and directory extractor
│   │   └── discover.py          # Discovery orchestrator (58 creator dataset seed)
│   │
│   ├── filtering/
│   │   └── classifier.py        # Qualification engine, rule-based checks, and reasoning logs
│   │
│   ├── enrichment/
│   │   └── enricher.py          # Profile enrichment, tier assignment, and "Not Found" handling
│   │
│   ├── personalization/
│   │   ├── prompts.py           # Structured prompts with strict word count boundaries
│   │   └── generator.py         # LLM connector (OpenAI/Groq) with fallback semantic generator
│   │
│   ├── sending/
│   │   ├── email_sender.py      # SMTP dispatch, sandbox simulator, and duplicate blocker
│   │   └── dm_manager.py        # Meta-compliant Instagram/TikTok DM staging workflow
│   │
│   └── tracking/
│       └── tracker.py           # SQLite outreach database and CSV tracker exporter
│
├── data/
│   ├── raw/
│   │   └── discovered_influencers.json   # 58 raw discovered creator profiles
│   ├── processed/
│   │   ├── filtered_influencers.json     # Classified profiles with pass/fail reasons
│   │   └── enriched_influencers.json     # Profiles enriched with demographics and angles
│   ├── outreach/
│   │   ├── personalized_messages.json    # Generated email and DM texts with word counts
│   │   └── outreach_tracker.csv          # Section 7.D required outreach tracking CSV
│   ├── influencer_dataset.csv            # Section 7.B required dataset CSV (9 standard columns)
│   └── outreach_history.db               # SQLite database of historical outreaches
│
├── tests/
│   └── test_pipeline.py         # Automated pytest test suite for all stages
│
├── main.py                      # Master CLI runner executing all 6 pipeline stages
├── dashboard.py                 # Interactive Streamlit Web UI dashboard
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # System documentation
```

---

## Technology Stack & Tools Used

| Layer | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12 / 3.14 | Core language for modular implementation |
| **Primary AI / LLM** | `cohere` (Command R+) | Highly personalized collaboration pitches via Cohere API |
| **Secondary AI / LLMs**| `groq`, `openai` | Dynamic multi-provider support (LLaMA 3.3 / GPT-4o-mini) |
| **Fallback AI Engine** | Python Dynamic Semantic Synthesizer | Guarantees 100% functionality even without API keys |
| **Data Processing** | `pandas`, `pydantic` | Data manipulation, transformation, and CSV export |
| **Web Dashboard** | `streamlit` | Interactive UI for non-technical review and demo |
| **CLI Formatting** | `rich` | Beautiful console tables, status indicators, and logs |
| **Database** | SQLite (`sqlite3`) | Persistent storage, history tracking, and duplicate prevention |
| **Sending Engine** | `smtplib`, `email.mime` | Standard RFC 5322 email transmission + simulation sandbox |
| **Testing** | `pytest` | Automated testing for counts, bounds, and business rules |

---

## Methodology & Logic Breakdown

### 1. Influencer Discovery
- **Niche Chosen:** Fashion & Beauty (Skincare, Clean Beauty, Minimalist Style, Haircare, Men's Grooming).
- **Channels:** Instagram, TikTok, and YouTube.
- **Criteria:** Fetches 58 creator profiles (exceeds the 50 minimum test run requirement).
- **Data Captured:** Name, Platform, Profile URL, Follower count, Engagement rate, Content themes, Recent post context, Public contact email (or `"Not Found"`), Bio, Website, Audience age/gender/geography.

### 2. Filtering & Classification
Every discovered profile is evaluated by `evaluate_influencer()` against 5 objective rules:
1. **Category Match:** Must belong to `Fashion & Beauty`. If from `Crypto` or `Technology`, immediately disqualified.
2. **Follower Range:** Must be within `5,000` to `100,000` followers (micro-influencer definition). Flagged if `< 5k` or `> 100k`.
3. **Engagement Rate:** Must be $\ge 2.0\%$. Creators with low engagement are rejected.
4. **Brand-Fit & Spam Filtering:** Rejects profiles containing spam or blacklisted keywords (e.g. `giveaways only`, `f4f`, `crypto bot`).
5. **Clear Audit Trail:** Every record contains an explicit `status` (`PASSED` or `FAILED`) and a descriptive `filter_reason` (e.g., *"Disqualified: Engagement rate (0.8%) is below minimum threshold (2.0%)"*).

### 3. Profile Enrichment
Shortlisted creators are passed to `enrich_influencers()`:
- **Mandatory Fields Verified:** Influencer Name, Platform, Profile URL, Follower Count, Engagement Rate, Category/Niche, Content Themes, Contact Email.
- **Missing Email Policy:** If an email is not present, it is explicitly marked `"Not Found"`. Guessing or generating fake emails is strictly prohibited.
- **Audience Context:** Age distributions, gender split, and primary geographies are mapped.
- **Derived Insights:** Calculates estimated active reach (`followers * engagement%`), assigns creator tier (`Early Micro`, `Mid Micro`, `Senior Micro`), and recommends the best collaboration angle (e.g., *UGC short-form video*, *30-day glow routine sponsorship*, *Styling lookbook integration*).

### 4. Message Personalization & Word Counts
Two outreach messages are dynamically generated for each qualified creator:
- **A. Email Collaboration Pitch:**
  - **Constraint:** Strictly between **60 and 90 words**.
  - **Personalization Signals:** Addresses creator by name, references specific recent post content, connects to their core theme, proposes tailored collaboration angle, highlights mutual value (product gifting + compensation), and includes a clear call to action.
- **B. Instagram / TikTok DM:**
  - **Constraint:** Strictly between **15 and 30 words**.
  - **Tone:** Conversational, punchy, respectful, and direct.
- **AI Engine:**
  - Connects to Groq (`llama-3.3-70b-versatile`) or OpenAI (`gpt-4o-mini`) if API keys are set in `.env`.
  - Includes a built-in **Dynamic Semantic Synthesizer** that dynamically constructs custom, non-templated messages respecting exact word limits if running offline or without API credits.

### 5. Sending Layer & Compliance
- **Recipient Selection:** Automatically filters to only send emails to creators with verified emails (skips `"Not Found"`).
- **Duplicate Prevention:** Before dispatching, the email is checked against historical records in `outreach_history.db`. If previously contacted, dispatch is aborted with `DUPLICATE_PREVENTED`.
- **Email Delivery:** Supports real SMTP (Gmail, SendGrid, Mailgun) or safe `simulation` sandbox mode (default, prevents accidental mass emailing during testing).
- **Instagram DM Compliance:** Because direct DM automation on Instagram/TikTok violates Meta/ByteDance terms of service without approved enterprise partner APIs, the system stages DMs into an operator-ready queue with one-click copy buttons and simulated dispatch logging.

### 6. Outreach Tracker (Section 7.D)
Maintains full tracking of outreach activities:
- Fields: `Influencer`, `Email`, `Platform`, `Channel`, `Message Generated`, `Sent`, `Date`, `Status`, `Collaboration Angle`, `Detail`.
- Exported to `data/outreach/outreach_tracker.csv` and stored in SQLite `data/outreach_history.db`.

---

## Setup Instructions

### 1. Clone & Navigate to Project
```bash
cd OutreachAI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: If you want to use live LLMs, add your `OPENAI_API_KEY` or `GROQ_API_KEY`. If left blank, the system automatically uses its dynamic synthesizer with zero errors!)*

---

## How to Run the Project

### Option A: Run the End-to-End CLI Pipeline
Executes all 6 stages and updates all JSON, CSV, and SQLite datasets:
```bash
python main.py
```

### Option B: Launch the Interactive Web Dashboard
Provides a visual dashboard with real-time filters, demographic inspection, and message previews:
```bash
streamlit run dashboard.py
```
*(The dashboard opens automatically at `http://localhost:8501`)*

### Option C: Run the Automated Pytest Suite
```bash
python -m pytest tests/test_pipeline.py -v
```

---

## Datasets Generated

| File Path | Description | Spec Section |
| :--- | :--- | :--- |
| `data/influencer_dataset.csv` | Full dataset of 58 discovered influencers with 9 standard columns | Section 7.B |
| `data/outreach/personalized_messages.json` | Generated personalized email pitch and IG DM for each creator | Section 7.C |
| `data/outreach/outreach_tracker.csv` | Outreach log tracking delivery, status, channel, and dates | Section 7.D |
| `data/processed/filtered_influencers.json` | Complete classification log with pass/fail reasons | Section 2 |
| `data/processed/enriched_influencers.json` | Enriched records with demographics and collaboration angles | Section 3 |
| `data/outreach_history.db` | SQLite database for ACID persistence and deduplication | Section 5 |

---

## Limitations & Scaling to 500+ Influencers

1. **API Rate Limits:**
   - *Current:* 58 influencers are processed in sub-second time.
   - *Scaling to 500+:* Use asynchronous batching (`asyncio`, `httpx`, or Celery / Redis queue) with rate-limiting backoffs for LLM and directory APIs.
2. **Social Media Scraping Governance:**
   - Direct scraping of social platforms can face anti-bot barriers (Cloudflare, IP blocks).
   - *Production Solution:* Connect to official Meta Graph API (Instagram Creator API) or partner APIs (Modash, Phyllo, Aspire).
3. **Email Deliverability:**
   - Direct cold sending of 500+ emails from a single address hurts domain reputation.
   - *Production Solution:* Integrate mailbox warmup, SPF/DKIM/DMARC authentication, and staggered sending (e.g. 50 emails/day per inbox via Instantly or Smartlead).
