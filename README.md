# 🏋️‍♂️ AI Expert Fitness Coach Assistant (Google ADK)

An expert, multimodal AI fitness and CrossFit coach assistant built with the **Google Agent Development Kit (ADK)** ([adk.dev](https://adk.dev)) and powered by **Gemini 3.6 Flash**.

---

## 🌟 Key Architecture & Capabilities

1. **Multi-Agent Orchestration (ADK 2.0)**:
   - **`FitnessOrchestratorAgent`**: Lead coach coordinating intents and multi-agent responses.
   - **`ProfileVaultAgent`**: Secure storage of biometrics, injury history, geolocation, and dietary restrictions with **AES-256-GCM + Cloud KMS Envelope Encryption** and in-memory PII sanitization.
   - **`AdaptivePlannerAgent`**: Dynamic daily workout programming adapted to **localized real-time weather** (heat index, rain) and **pre-session readiness check-ins** (energy 1-5, sleep quality, muscle soreness).
   - **`SessionAnalystAgent`**: **Post-session check-ins** (RPE 1-10, muscle fatigue, acute pain screeners), **historical workout ledger** with natural language date queries (*"What did I do last Tuesday?"*), and longitudinal **tonnage/RPE trend analysis**.
   - **`MovementResearchAgent`**: Verified CrossFit movement mechanics (9 foundational movements, Olympic lifts, gymnastics), points of performance, common faults, scaling ladders, and verified YouTube video demo links.
   - **`NutritionFuelingAgent`**: ISSN sports nutrition calculator (BMR, METs workout burn, macro targets) and **post-workout recipe generator** (Quick Smoothies < 5 min & Whole-Food Power Meals 15-20 min) matching dietary styles (Paleo, Vegan, Omnivore, etc.).
   - **`GamificationAgent`**: Octalysis motivation engine managing XP, levels, PR tracking, weekly quests, and streak protection with **Monthly Streak Freeze Tokens**.

2. **100% Gemini Flash Tier**:
   - Standardized on **`gemini-3.6-flash`** for low latency, sub-second responses, and Google AI Studio Free Tier compatibility.

3. **Cloud Run Ready with Web UI**:
   - Ready for local interactive development via `adk web` or one-line deployment to **Google Cloud Run** using `--with_ui`.

---

## 📁 Project Structure

```
fitness-coach/
├── fitness_coach/                # Primary ADK agent package (valid Python identifier)
│   ├── __init__.py
│   └── agent.py                  # Exposes root_agent for ADK Web & Runners
├── agents/                       # Specialized domain sub-agents
│   ├── orchestrator.py           # Head coach orchestrator
│   ├── profile_vault.py          # Encrypted biometrics vault
│   ├── adaptive_planner.py       # Pre-checkin & weather-adaptive programming
│   ├── session_analyst.py        # Post-checkin, date history & trends
│   ├── movement_research.py      # CrossFit movement standards & videos
│   ├── dietitian.py              # Sports nutrition & post-workout recipes
│   └── gamification.py           # XP, levels, streaks & PR badges
├── tools/                        # Domain calculation & crypto engines
│   ├── crypto_tools.py           # KMS envelope encryption & PII sanitization
│   ├── readiness_tools.py        # Pre/Post-session check-in scoring matrices
│   ├── periodization_tools.py    # 1RM estimator & dynamic workout scaler
│   ├── nutrition_tools.py        # BMR, TDEE, METs & recipe engine
│   └── history_tools.py          # Date-based workout retrieval & trend engine
├── mcp_servers/                  # MCP & integrated external services
│   ├── weather_service.py        # Localized weather, Heat Index & AQI
│   ├── crossfit_knowledge.py     # Verified movements & benchmark WODs catalog
│   └── gamification_engine.py    # XP, streaks, badges & quests state
├── data/                         # Verified seed databases
│   ├── movements_seed.json       # Foundational CrossFit movements & video demos
│   └── benchmark_wods.json       # Benchmark WODs (Fran, Cindy, Murph, etc.)
├── config/
│   └── settings.py               # Global settings & model configurations (loads .env)
├── tests/                        # Comprehensive test suite (14 passing tests)
│   ├── test_crypto.py
│   ├── test_history_and_trends.py
│   ├── test_nutrition_recipes.py
│   ├── test_readiness_and_planner.py
│   ├── test_weather_adaptation.py
│   └── test_gamification.py
├── .env.example                  # Template for secrets and environment variables
├── .gitignore                    # Git ignore file (secures .env, venv, caches, .adk)
├── Dockerfile                    # Production container image
├── deploy.sh                     # Google Cloud Run deployment script
├── requirements.txt
└── pyproject.toml
```

---

## 🚀 Quickstart Guide

### 1. Installation & Environment Setup

```bash
# Clone and enter directory
cd fitness-coach-assistant

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables (`.env`)

Create your `.env` file from the provided template:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```ini
# Google AI Studio API Key (Free tier): https://aistudio.google.com/
# Either GOOGLE_API_KEY or GEMINI_API_KEY is automatically recognized:
GOOGLE_API_KEY=your_gemini_api_key_here

# Model Selection (defaults to gemini-3.6-flash)
GEMINI_MODEL=gemini-3.6-flash
GEMINI_FAST_MODEL=gemini-3.6-flash

# Optional GCP Settings
GCP_PROJECT=fitness-coach-dev
GCP_REGION=us-central1
```

> [!NOTE]
> `.env` is ignored by git to protect your credentials. Settings are automatically loaded via `python-dotenv`.

### 3. Run Automated Test Suite

```bash
pytest -v
```
*Executes all unit and integration tests verifying crypto, weather adaptation, recipe generation, date queries, and gamification.*

### 4. Run End-to-End CLI Simulation

```bash
python3 main.py
```
*Simulates the full athlete lifecycle: onboarding $\rightarrow$ pre-checkin $\rightarrow$ weather adaptation $\rightarrow$ movement research $\rightarrow$ post-checkin $\rightarrow$ refuel recipes $\rightarrow$ history recall $\rightarrow$ gamification XP.*

### 5. Test Single-Turn Query via CLI

```bash
python3 -m google.adk.cli run fitness_coach "hello, what is today's session?"
```

### 6. Launch Interactive Web UI (ADK Web)

```bash
# Launch ADK Web Chat UI
python3 -m google.adk.cli web --port 8080
```
- Open **`http://localhost:8080`** in your browser.
- Select **`fitness_coach`** from the agent dropdown.
- Start chatting with your coach!

> [!TIP]
> For verbose debugging logs in the terminal, run: `python3 -m google.adk.cli web -v`. ADK also streams detailed logs to `/tmp/agents_log/agent.latest.log`.

---

## ☁️ Google Cloud Deployment (Cloud Run)

As prerequisites: 
- Install [Google Cloud CLI](https://docs.cloud.google.com/sdk/docs/install-sdk#latest-version). 
- Activate billing on your GCP project in [AI Studio](https://aistudio.google.com/).
- Activate [service account](https://docs.cloud.google.com/sdk/gcloud/reference/auth/activate-service-account)

### Method 1: Using the Deployment Script
```bash
export GCP_PROJECT="your-gcp-project-id"
export GCP_REGION="us-central1"
export GEMINI_API_KEY="your-ai-studio-project-api-key"
chmod +x deploy.sh
./deploy.sh
```

### Method 2: Using the ADK CLI (TODO: To be reviewed as it does not deploy properly for now)

```bash
> gcloud iam service-accounts keys create /path/key.json --iam-account="iam-account-email"
> gcloud auth activate-service-account SERVICE_ACCOUNT@DOMAIN.COM --key-file=/path/key.json --project="project-id"
```
- Import project linked to service account in [AI studio](https://aistudio.google.com/docs/api-key#import-projects)
- Add entry for [GOOGLE_API_KEY](https://adk.dev/deploy/cloud-run/)

```bash
export GCP_PROJECT="your-gcp-project-id"
adk deploy cloud_run \
  --project="$GCP_PROJECT" \
  --region="us-central1" \
  --service_name="fitness-coach-assistant" \
  --with_ui \
  ./
```

---

## 🛡️ Security, Privacy & Safety Highlights
- **Cloud KMS Envelope Encryption**: All sensitive biometrics (age, weight, height, injuries, health history) are encrypted at rest using individual DEKs wrapped by Cloud KMS.
- **In-Memory PII Sanitization**: LLMs receive strictly anonymized tokens without personal names or emails.
- **Medical Disclaimer Guardrails**: Automatic halt and physical therapy disclaimer if acute joint or tendon pain is flagged during post-session check-ins.
- **Anti-Burnout Gamification**: Streak protection tokens prevent breaking habit streaks during necessary rest or recovery days.

## Troubleshoot

- Activate [Cloud Run Admin API](https://console.cloud.google.com/apis/api/run.googleapis.com) when having error `(gcloud.run.deploy) PERMISSION_DENIED: Cloud Run Admin API has not been used in project...`
- Activate [Cloud Build API](https://console.cloud.google.com/apis/library/cloudbuild.googleapis.com) when having error `(gcloud.run.deploy) PERMISSION_DENIED: Cloud Build API has not been used in project...`
