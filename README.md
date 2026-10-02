# OutreachAI - Automated Micro-Influencer Outreach System

> Enterprise-grade pipeline for automated micro-influencer discovery, intelligent filtering, profile enrichment, and AI-personalized outreach generation at scale.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Core Architecture and Innovations](#2-core-architecture-and-innovations)
3. [System Design](#3-system-design)
4. [Folder Structure](#4-folder-structure)
5. [Technology Stack](#5-technology-stack)
6. [Installation and Operation](#6-installation-and-operation)
7. [Pipeline Deep Dive](#7-pipeline-deep-dive)
8. [API and Configuration Reference](#8-api-and-configuration-reference)
9. [Data Outputs and Schema](#9-data-outputs-and-schema)
10. [Testing](#10-testing)
11. [Scalability and Production Roadmap](#11-scalability-and-production-roadmap)
12. [APIs and Tools Used](#12-apis-and-tools-used)

---

## 1. Executive Summary

**OutreachAI** is a six-stage automated pipeline that transforms raw social media creator data into production-ready, AI-personalized collaboration outreach in a single command.

| Metric | Value |
|:---|:---|
| Creators Discovered | **58** (surpasses 50 minimum requirement) |
| Influencers Qualified (Passed Filter) | **53** (91.4% pass rate) |
| Profiles Enriched | **53** |
| Personalized Email Pitches Generated | **53** (60-90 words each) |
| Personalized Instagram/TikTok DMs Generated | **53** (15-30 words each) |
| Primary AI Engine | **Cohere Command R** (command-r-08-2024) |
| Fallback Engine | Built-in Dynamic Semantic Synthesizer |
| Deduplication | SQLite ACID-persistent history database |
| Outreach Compliance | Simulation sandbox (no accidental live sends) |

**Target Niche:** Fashion and Beauty (Skincare, Clean Beauty, Minimalist Fashion, Haircare, Mens Grooming)  
**Target Platforms:** Instagram, TikTok, YouTube  
**Micro-Influencer Definition:** 5,000 to 100,000 followers with minimum 2.0 percent engagement rate

---

## 2. Core Architecture and Innovations

### 2.1 Six-Stage Modular Pipeline

The system is decomposed into six independently testable, loosely-coupled stages connected by typed Python interfaces:

```
Discovery -> Filtering -> Enrichment -> Personalization -> Sending -> Tracking
```

Each stage reads structured JSON from the previous stage output and writes its own artifact, making every layer independently replaceable without affecting adjacent components.

### 2.2 Key Technical Innovations

**Dual-Engine AI Personalization**

- Primary: Cohere Command R API with structured JSON output enforcement via prompt engineering
- Fallback: A deterministic Dynamic Semantic Synthesizer that produces unique, non-templated messages using creator-specific signals even when offline or API credits are exhausted
- Zero failure mode: the system always produces output regardless of API availability

**Structured Prompt Engineering**

- Word-count hard constraints enforced both in the LLM prompt (`build_unified_outreach_prompt`) and post-generation via `normalize_email_length()` and `trim_to_word_limit()`
- JSON-only response enforcement prevents hallucinated freeform output
- Emoji stripping via `strip_emojis()` ensures clean, professional copy

**Audit-First Filtering**

- Every evaluated influencer (passed or failed) carries an explicit `status`, `filter_reason`, and `brand_fit_score` (0-100)
- All rejection decisions are human-readable, e.g., "Disqualified: Engagement rate (0.8%) is below minimum threshold (2.0%)"

**ACID-Persistent Deduplication**

- SQLite database (`outreach_history.db`) prevents re-contacting any influencer across pipeline runs
- Pre-flight duplicate check runs before each email dispatch attempt

**Meta/ByteDance TOS-Compliant DM Workflow**

- Instagram and TikTok DMs are staged into an operator queue rather than auto-dispatched
- Prevents Terms of Service violations while maintaining full message generation and logging

---

## 3. System Design

### 3.1 High-Level Data Flow

```
[ Public Creator Directories / Social Platforms / UGC Marketplaces ]
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 1: DISCOVERY                                                |
|  src/discovery/discover.py + scraper.py                           |
|  - Loads 58 creator profiles (Instagram, TikTok, YouTube)         |
|  - Fields: name, handle, platform, URL, followers, engagement,    |
|    content_themes, bio, email, website, audience demographics     |
|  Output: data/raw/discovered_influencers.json                     |
+--------------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 2: FILTERING AND CLASSIFICATION                             |
|  src/filtering/classifier.py                                       |
|  Rule 1: Category must match "Fashion and Beauty"                  |
|  Rule 2: Followers in range 5,000 to 100,000                       |
|  Rule 3: Engagement rate >= 2.0 percent                            |
|  Rule 4: Bio must not contain disqualified keywords                |
|  Rule 5: Brand-fit score from keyword corpus analysis (0-100)     |
|  Output: data/processed/filtered_influencers.json                 |
+--------------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 3: PROFILE ENRICHMENT                                       |
|  src/enrichment/enricher.py                                        |
|  - Email validation: real vs "Not Found" (no fabrication policy)  |
|  - Creator tier: Early Micro / Mid Micro / Senior Micro            |
|  - Active reach: followers x engagement_rate                       |
|  - Collaboration angle: platform and theme-derived recommendation  |
|  Output: data/processed/enriched_influencers.json                 |
+--------------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 4: AI PERSONALIZATION                                       |
|  src/personalization/generator.py + prompts.py                    |
|  - Primary: Cohere Command R (command-r-08-2024)                   |
|  - Fallback: Dynamic Semantic Synthesizer                          |
|  - Email pitch: 60-90 words, 3-paragraph structured format        |
|  - Instagram DM: 15-30 words, punchy and conversational           |
|  Output: data/outreach/personalized_messages.json                 |
+--------------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 5: SENDING LAYER                                            |
|  src/sending/email_sender.py + dm_manager.py                      |
|  - Duplicate pre-flight check against SQLite history               |
|  - Email: SMTP via Gmail or simulation sandbox (default)           |
|  - DM: Operator-staged queue (TOS-compliant)                       |
+--------------------------------------------------------------------+
                              |
                              v
+--------------------------------------------------------------------+
|  STAGE 6: TRACKING AND REPORTING                                   |
|  src/tracking/tracker.py                                           |
|  - SQLite: ACID-persistent outreach log (deduplication source)    |
|  - CSV: data/outreach/outreach_tracker.csv (human-readable)       |
|  - Dashboard: Streamlit UI (dashboard.py)                         |
+--------------------------------------------------------------------+
```

### 3.2 AI Personalization Decision Tree

```
generate_personalized_messages(influencer)
          |
          +--[ COHERE_API_KEY present? ]--YES--> call_cohere_llm(prompt)
          |                                            |
          |                                     JSON parse and validate
          |                                            |
          |                                     strip_emojis()
          |                                     normalize_email_length()  [60-90 words]
          |                                     trim_to_word_limit()      [15-30 words]
          |                                            |
          |                                     [ Valid output? ]--NO---> Fallback
          |                                            |
          |                                           YES
          |                                            v
          |                                    engine_used = "Cohere Command R"
          |
          +--[ No API key / Rate limited / Parse fail ]
                        |
                        v
          generate_dynamic_fallback_messages()
                   Rule-based synthesis using creator-specific signals:
                   - influencer name (first name extracted)
                   - recent_post_summary field
                   - content_themes[0] primary theme
                   - suggested_collaboration angle
                        |
                   engine_used = "Dynamic Semantic Synthesizer"
```

---

## 4. Folder Structure

```
OutreachAI/
|
+-- config/
|   +-- settings.py              # Path constants, env vars, API keys, defaults
|   +-- criteria.py              # Filtering thresholds and niche keyword lists
|
+-- src/
|   +-- discovery/
|   |   +-- scraper.py           # Profile parser and directory extractor helpers
|   |   +-- discover.py          # 58-creator curated dataset + run_discovery()
|   |
|   +-- filtering/
|   |   +-- classifier.py        # evaluate_influencer(), filter_influencers(), brand scoring
|   |
|   +-- enrichment/
|   |   +-- enricher.py          # enrich_single_profile(), determine_creator_tier()
|   |
|   +-- personalization/
|   |   +-- prompts.py           # build_unified_outreach_prompt() -- structured LLM prompt
|   |   +-- generator.py         # generate_personalized_messages(), call_cohere_llm()
|   |
|   +-- sending/
|   |   +-- email_sender.py      # dispatch_email_outreach() -- SMTP and simulation mode
|   |   +-- dm_manager.py        # prepare_dm_queue(), dispatch_simulated_dm()
|   |
|   +-- tracking/
|       +-- tracker.py           # SQLite CRUD, log_outreach_entry(), CSV export
|
+-- data/
|   +-- raw/
|   |   +-- discovered_influencers.json    # Stage 1 output: 58 raw profiles
|   +-- processed/
|   |   +-- filtered_influencers.json     # Stage 2 output: classified with pass/fail
|   |   +-- enriched_influencers.json     # Stage 3 output: enriched profiles
|   +-- outreach/
|   |   +-- personalized_messages.json   # Stage 4 output: AI-generated messages
|   |   +-- outreach_tracker.csv         # Stage 6 CSV export (assignment deliverable)
|   +-- influencer_dataset.csv           # Full 58-creator dataset (assignment deliverable)
|   +-- outreach_history.db              # SQLite deduplication and history database
|
+-- tests/
|   +-- test_pipeline.py         # pytest suite covering all 6 pipeline stages
|
+-- main.py                      # Master CLI: executes all 6 stages end-to-end
+-- dashboard.py                 # Streamlit interactive web dashboard
+-- requirements.txt             # Pinned Python dependencies
+-- .env.example                 # Environment variable configuration template
+-- .env                         # Local secrets (gitignored)
+-- .gitignore
+-- README.md
```

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|:---|:---|:---|:---|
| Language | Python | 3.12+ | Core application runtime |
| **Primary AI / LLM** | **Cohere API** (command-r-08-2024) | >=5.0.0 | Personalized outreach message generation |
| Fallback AI | Dynamic Semantic Synthesizer | Built-in | Guaranteed message output with zero API dependency |
| Data Processing | pandas | >=2.0.0 | DataFrame operations, CSV export, dataset assembly |
| Data Validation | pydantic | >=2.0.0 | Schema validation and type safety |
| Web Dashboard | streamlit | >=1.30.0 | Interactive UI for pipeline results and demo |
| CLI Formatting | rich | >=13.0.0 | Console tables, progress indicators, stage logs |
| HTTP Client | requests | >=2.30.0 | General API communication |
| HTTP Client (Cohere) | httpx | Bundled with cohere | Cohere SDK transport with configurable timeout |
| Database | SQLite (sqlite3) | Stdlib | ACID-persistent outreach history and deduplication |
| Email Sending | smtplib + email.mime | Stdlib | SMTP email dispatch and simulation sandbox |
| Testing | pytest | >=8.0.0 | Automated unit and integration test suite |
| Environment Config | python-dotenv | >=1.0.0 | .env file loading |

> **Primary AI Constraint:** Only the Cohere API is used for LLM-based personalization. No OpenAI or Groq keys are required. The system activates its built-in Dynamic Semantic Synthesizer automatically when the Cohere API is unavailable.

---

## 6. Installation and Operation

### 6.1 Prerequisites

- Python 3.12 or higher
- pip package manager
- Cohere API key (optional -- the system operates fully without one via the fallback engine)

### 6.2 Clone and Setup

```bash
# Navigate to project directory
cd OutreachAI

# Install all dependencies
pip install -r requirements.txt
```

### 6.3 Environment Configuration

```bash
# Copy the template
cp .env.example .env
```

Edit `.env` with your configuration values:

```ini
# AI Personalization (Cohere) -- optional but recommended for best output
COHERE_API_KEY=your_cohere_api_key_here

# Email Sending -- optional (simulation mode works without these)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# Brand Configuration
SENDER_NAME=GlowAura Brand Collaborations
BRAND_NAME=GlowAura Skincare
CAMPAIGN_TYPE=UGC content creation

# Sending Mode: "simulation" (safe default) or "live"
SEND_MODE=simulation
```

> If `COHERE_API_KEY` is not set, the Dynamic Semantic Synthesizer activates automatically. No setup is required to run a full end-to-end demonstration.

### 6.4 Running the System

**Option A -- Full CLI Pipeline (Recommended)**

Executes all 6 stages and populates all JSON, CSV, and SQLite outputs:

```bash
python main.py
```

Expected console output:

```
====================================================
 Micro-Influencer Outreach System - Pipeline Run
====================================================

Step 1: Running Influencer Discovery...
[OK] Discovered 58 influencer profiles.

Step 2: Filtering and Classifying Candidates...
[OK] Total Evaluated: 58
[OK] Passed: 53
[X]  Failed: 5
[OK] Pass Rate: 91.4%

Step 3: Enriching Shortlisted Creator Profiles...
[OK] Enriched 53 profiles with metrics, angles, and demographics.
[OK] Profiles with valid email: 50 | Missing email: 3

Step 4: Generating AI-Personalized Outreach (Email + DM)...
  [1/53] Personalized: Maya Lin (via Cohere Command R)
  [2/53] Personalized: Sofia Reyes (via Cohere Command R)
  ...
  [53/53] Personalized: Victoria Stone (via Cohere Command R)

Step 5: Executing Outreach Sending Layer...
Step 6: Updating Outreach Tracker...
[OK] Outreach tracker updated at: data/outreach/outreach_tracker.csv
```

**Option B -- Interactive Web Dashboard**

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501`. Dashboard features:
- Real-time influencer table with multi-field filters
- Pass/fail classification breakdown with reasoning per creator
- Per-influencer message preview (email pitch and DM)
- Full outreach tracker with dispatch history

**Option C -- Automated Test Suite**

```bash
python -m pytest tests/test_pipeline.py -v
```

---

## 7. Pipeline Deep Dive

### Stage 1: Influencer Discovery

**Files:** `src/discovery/discover.py`, `src/discovery/scraper.py`  
**Entry Point:** `run_discovery() -> List[Dict]`

- Loads a curated dataset of 58 micro-influencer profiles across Instagram, TikTok, and YouTube in the Fashion and Beauty niche
- Profile fields captured: `name`, `handle`, `platform`, `profile_url`, `follower_count`, `engagement_rate`, `category`, `sub_niche`, `content_themes`, `bio`, `email`, `website`, `recent_post_summary`, `audience_age`, `audience_gender`, `audience_geography`
- `scraper.py` provides `parse_creator_profile()` as a helper for future live scraping or directory API integration
- Saves raw JSON to disk for independent audit and reprocessing

**Output:** `data/raw/discovered_influencers.json` (58 profiles)

---

### Stage 2: Filtering and Classification

**File:** `src/filtering/classifier.py`  
**Functions:** `evaluate_influencer()`, `filter_influencers()`, `calculate_brand_fit_score()`

Five sequential gate checks applied per influencer:

| Gate | Qualifying Rule | Rejection Reason Format |
|:---|:---|:---|
| 1 | Bio must not contain disqualified keywords | "Bio matches flagged keyword '...'" |
| 2 | `category` must equal "Fashion and Beauty" | "Category '...' does not match target niche" |
| 3 | `follower_count` >= 5,000 | "Follower count (...) is below micro-influencer minimum" |
| 4 | `follower_count` <= 100,000 | "Follower count (...) exceeds micro-influencer threshold" |
| 5 | `engagement_rate` >= 2.0 | "Engagement rate (...)% is below minimum threshold (2.0%)" |

Brand-fit score calculation:

```
brand_fit_score = min(100, 50 + (count_of_matched_brand_keywords * 10))
```

Every profile receives an explicit `status` (PASSED or FAILED), a human-readable `filter_reason`, and a numeric `brand_fit_score`.

**Output:** `data/processed/filtered_influencers.json`  
**Result:** 53 passed / 5 failed (91.4% pass rate)

---

### Stage 3: Profile Enrichment

**File:** `src/enrichment/enricher.py`  
**Functions:** `enrich_single_profile()`, `determine_creator_tier()`, `suggest_collaboration_angle()`

Derived fields added to each qualified profile:

| Field | Derivation Logic |
|:---|:---|
| `creator_tier` | followers < 25k: Early Micro; 25k-50k: Mid Micro; 50k-100k: Senior Micro |
| `estimated_active_engagement` | int(followers x (engagement_rate / 100)) |
| `suggested_collaboration` | Lookup table driven by platform type and primary content themes |
| `has_valid_email` | True only if the email field contains "@" |
| `enrichment_status` | COMPLETE or PARTIAL_NO_EMAIL |

**Email Policy:** If an email field is missing or does not contain "@", it is explicitly set to "Not Found". No fabrication of contact information is permitted under any circumstance.

**Output:** `data/processed/enriched_influencers.json` (53 profiles)

---

### Stage 4: AI Personalization

**Files:** `src/personalization/generator.py`, `src/personalization/prompts.py`  
**Entry Point:** `personalize_all(enriched_list) -> List[Dict]`

Two messages are generated per influencer:

**Email Collaboration Pitch**
- Word count constraint: 60 to 90 words (enforced via `normalize_email_length()` post-generation)
- Three-paragraph structure: (1) appreciation of specific recent post content, (2) campaign introduction with product gifting plus compensation offer, (3) CTA to review the brief this week
- Subject line: under 10 words, collaboration-specific, professional tone

**Instagram / TikTok Direct Message**
- Word count constraint: 15 to 30 words (enforced via `trim_to_word_limit()`)
- Tone: conversational, punchy, no corporate jargon, direct call to action

**AI Engine Priority:**
1. Cohere `command-r-08-2024` via `call_cohere_llm()` with JSON-structured output parsing
2. `generate_dynamic_fallback_messages()` activated on API failure, rate limit, or JSON parse error

**Output:** `data/outreach/personalized_messages.json` (53 records)

---

### Stage 5: Sending Layer

**Files:** `src/sending/email_sender.py`, `src/sending/dm_manager.py`

- `dispatch_email_outreach()`: runs deduplication pre-check against SQLite history, then dispatches via SMTP or records to simulation log
- `prepare_dm_queue()`: stages all DMs with full influencer metadata for operator-controlled dispatch
- `dispatch_simulated_dm()`: logs simulated send with timestamp and status for full audit trail

Default `SEND_MODE=simulation` prevents accidental live sends during evaluation or development environments.

---

### Stage 6: Outreach Tracking

**File:** `src/tracking/tracker.py`

- `log_outreach_entry()`: inserts each outreach record into the SQLite `outreach_history` table
- `get_contacted_emails()`: returns the full set of previously contacted emails for deduplication logic
- `export_outreach_tracker_csv()`: exports complete history to `data/outreach/outreach_tracker.csv`

**Tracker CSV Columns:** `Influencer`, `Email`, `Platform`, `Channel`, `Message Generated`, `Sent`, `Date`, `Status`, `Collaboration Angle`, `Detail`

---

## 8. API and Configuration Reference

### Environment Variables (.env)

| Variable | Required | Default | Description |
|:---|:---|:---|:---|
| `COHERE_API_KEY` | Optional | (empty) | Cohere API key for Command R personalization engine |
| `SMTP_HOST` | Optional | smtp.gmail.com | SMTP server hostname |
| `SMTP_PORT` | Optional | 587 | SMTP server port number |
| `SMTP_USER` | Optional | (empty) | Sender email address |
| `SMTP_PASSWORD` | Optional | (empty) | Gmail App Password (not the account password) |
| `SENDER_NAME` | Optional | GlowAura Partnerships | Display name used in outgoing emails |
| `BRAND_NAME` | Optional | GlowAura Beauty | Brand name injected into all outreach copy |
| `CAMPAIGN_TYPE` | Optional | UGC content creation | Default campaign label for outreach messages |
| `SEND_MODE` | Optional | simulation | Set to "live" to enable real SMTP dispatch |

### Filtering Criteria (config/criteria.py)

| Parameter | Default Value | Description |
|:---|:---|:---|
| `MIN_FOLLOWERS` | 5,000 | Minimum follower count for micro-influencer classification |
| `MAX_FOLLOWERS` | 100,000 | Maximum follower count upper threshold |
| `MIN_ENGAGEMENT_RATE` | 2.0 | Minimum engagement rate in percent for qualification |
| `TARGET_NICHE` | "Fashion and Beauty" | Required category value for acceptance |

---

## 9. Data Outputs and Schema

### influencer_dataset.csv (Assignment Deliverable -- Section 7.B)

Complete 58-creator dataset with 9 standardized columns exported after filtering:

| Column | Type | Description |
|:---|:---|:---|
| Name | string | Creator full name |
| Platform | string | Instagram, TikTok, or YouTube |
| Followers | integer | Total follower count |
| Engagement | string | Engagement rate value |
| Niche | string | Content category |
| Email | string | Verified contact email or "Not Found" |
| Profile URL | string | Direct profile URL |
| Content Theme | string | Comma-separated theme tags |
| Status | string | PASSED or FAILED |

### personalized_messages.json (Assignment Deliverable -- Section 7.C)

Sample record schema:

```json
{
  "influencer_name": "Maya Lin",
  "platform": "Instagram",
  "profile_url": "https://instagram.com/mayalinglow",
  "email": "maya@mayalinglow.com",
  "follower_count": 42500,
  "engagement_rate": 4.8,
  "collaboration_angle": "30-day glow routine sponsorship and before/after",
  "email_subject": "Collaboration Opportunity: GlowAura Skincare x Maya",
  "email_body": "Hi Maya, ...",
  "email_word_count": 74,
  "instagram_dm": "Hi Maya, loved your skincare content. Open to a GlowAura collab this month?",
  "dm_word_count": 22,
  "engine_used": "Cohere Command R"
}
```

### outreach_tracker.csv (Assignment Deliverable -- Section 7.D)

Full dispatch log with columns: `Influencer`, `Email`, `Platform`, `Channel`, `Message Generated`, `Sent`, `Date`, `Status`, `Collaboration Angle`, `Detail`

---

## 10. Testing

The project ships with a pytest suite that validates all business rules and constraints:

```bash
python -m pytest tests/test_pipeline.py -v
```

| Test Case | Assertion |
|:---|:---|
| `test_discovery_count` | Discovered count is >= 50 |
| `test_all_pass_follower_bounds` | All passed influencers: 5,000 <= followers <= 100,000 |
| `test_all_pass_engagement_threshold` | All passed influencers: engagement_rate >= 2.0 |
| `test_email_word_count` | All email pitches: 60 <= word count <= 90 |
| `test_dm_word_count` | All DMs: 15 <= word count <= 30 |
| `test_no_fabricated_emails` | "Not Found" emails are never used in dispatch |
| `test_filter_audit_trail` | Every record carries status, filter_reason, and brand_fit_score |
| `test_deduplication` | Same influencer email is never dispatched more than once |

---

## 11. Scalability and Production Roadmap

### Current System Constraints

| Dimension | Current State | Production-Grade Solution |
|:---|:---|:---|
| Dataset size | 58 curated static profiles | Connect to Modash, Phyllo, or Meta Creator API for live discovery at scale |
| Throughput | Sequential single-thread processing | asyncio + httpx async batching with Celery/Redis distributed worker pool |
| Email volume | Simulation sandbox by default | Instantly.ai or Smartlead with inbox rotation, warmup, and SPF/DKIM/DMARC authentication |
| Scraping | Static JSON dataset | Playwright for JS-rendered pages with rotating residential proxy layer |
| LLM cost at scale | Per-call Cohere API | Batch prompt chaining, response caching, tenacity retry with exponential backoff |
| Storage | Local JSON files and SQLite | PostgreSQL for distributed persistence, AWS S3 for artifact and file storage |

### Recommended Production Architecture

```
[Creator Discovery Layer]  [Filter Engine]   [Enrichment API]   [LLM Batch Layer]
  Modash API             -> Rule Engine     -> Phyllo API      -> Cohere Batch API
  Collabstr API             + ML Brand Score   Contact DB         (async 50 parallel)
       |                         |                 |                     |
       +-------------------------+-----------------+---------------------+
                                         |
                             [PostgreSQL + Redis Pub-Sub]
                                         |
                          [Celery Worker Pool - 8 workers]
                                         |
                       [Instantly.ai / Smartlead SMTP Rotation]
                                         |
                         [Analytics Dashboard: Grafana / Metabase]
```

---

## 12. APIs and Tools Used

| Category | Tool / API / Library | Role in System |
|:---|:---|:---|
| **Primary AI / LLM** | Cohere API (command-r-08-2024) | AI-personalized email pitch and DM generation |
| **AI Fallback Engine** | Dynamic Semantic Synthesizer (built-in) | Guaranteed message output without any API dependency |
| **Data Processing** | pandas | DataFrame transformation, CSV export, dataset assembly |
| **Data Validation** | pydantic | Input/output type enforcement and schema safety |
| **Interactive Dashboard** | Streamlit | Web UI for result inspection and live demo |
| **CLI Output** | rich | Formatted console tables, colored progress indicators |
| **Relational Database** | SQLite (stdlib) | ACID-persistent outreach history and deduplication |
| **Email Dispatch** | smtplib + email.mime (stdlib) | SMTP email sending and simulation mode |
| **HTTP Communication** | requests | General HTTP requests and API calls |
| **HTTP SDK Transport** | httpx | Cohere SDK transport layer with configurable timeouts and retry control |
| **Testing Framework** | pytest | Automated assertions across all six pipeline stages |
| **Config Management** | python-dotenv | .env file parsing and environment variable management |
| **Creator Data Source** | Curated public profiles | 58 Instagram, TikTok, and YouTube micro-influencer profiles |
| **UGC Marketplaces Referenced** | Collabstr, Aspire, Grin | Discovery methodology and niche validation reference |

---

## License

All creator profile data is publicly sourced or curated for demonstration purposes.
