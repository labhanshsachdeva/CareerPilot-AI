# CareerPilot AI — Intelligent Job Copilot

CareerPilot AI is a portfolio-ready AI/ML engineering project that helps candidates map resume evidence to a target job description, identify gaps to investigate, prepare interview questions, and organise a 14-day improvement sprint.

## Why it stands out
- A multi-stage career workflow (Role Strategist → Evidence Analyst → Evidence Reviewer).
- Evidence-first outputs: it is designed not to invent candidate achievements.
- Optional OpenAI API integration with a deterministic keyword-based fallback.
- PDF/TXT resume input, Markdown report downloads, interview pack, and action plan.
- Unit tests and clear deployment guidance.
- Premium dark dashboard built with Streamlit and custom CSS.

## Features
1. **Resume Lab:** paste/upload a resume and add a target job description.
2. **Role-fit brief:** strengths, resume evidence, gaps to investigate, caveats, and next steps.
3. **Interview Studio:** role-specific questions with answer guidance when the API is configured; useful fallback questions otherwise.
4. **Action Plan:** editable 14-day checklist.
5. **Downloads:** Markdown reports suitable for keeping with an application.

## Architecture
```text
Resume PDF/TXT + Job Description
              |
              v
        Input / Parsing
              |
              v
       Role Strategist (LLM)
              |
              v
      Evidence Analyst (LLM)
              |
              v
      Evidence Reviewer (LLM)
              |
              v
 Resume Lab | Interview Studio | Action Plan
```

The current implementation uses one LLM call to produce the evidence-first analysis when the API is configured; the UI presents the three roles as an orchestration concept. For a stronger next iteration, split these into separately invoked, typed agents and log intermediate outputs. Do not describe the current version as three independent agents unless that orchestration is implemented.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app works without an API key using keyword matching and fallback interview questions. This mode is useful for local UI testing but is not a semantic evaluation model.

## Enable OpenAI
Set an environment variable before running the app:

**Windows PowerShell**
```powershell
$env:OPENAI_API_KEY="your-key-here"
streamlit run app.py
```

Or copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, then add your own key. Never commit a real key. Optionally set `OPENAI_MODEL` to a model available to your account.

## Tests
```bash
pytest -q
```

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository and push this folder (without API keys or private resumes).
2. Open Streamlit Community Cloud and create a new app from the repository.
3. Set the main file path to `app.py`.
4. Add `OPENAI_API_KEY` under the app's Secrets settings if you want live LLM features.
5. Deploy and test with sample, non-sensitive resume text.

## Evaluation and limitations
- The percentage is **keyword coverage**, not an ATS score, candidate quality score, or probability of getting hired.
- Keyword overlap can miss synonyms and can count a term without proving proficiency.
- LLM outputs can be incorrect. Review claims and keep only truthful resume content.
- Resume text is sent to the configured LLM provider when API analysis is enabled. Do not upload sensitive documents unless you understand the provider's data policies.
- This is a portfolio prototype, not a hiring decision system.

## Suggested roadmap
- Implement truly separate agents with Pydantic/JSON schema validation.
- Add synonym-aware matching and evidence span highlighting.
- Add retrieval over official role competency frameworks.
- Add evaluation fixtures for groundedness, coverage, latency, and cost.
- Add per-session data deletion and structured logs without storing resume contents.

## Project structure
```text
CareerPilot_AI/
├── app.py
├── career_engine.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
└── tests/
    └── test_career_engine.py
```
