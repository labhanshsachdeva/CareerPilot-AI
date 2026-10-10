"""Evidence-first resume analysis engine with optional OpenAI integration."""
import io, json, os, re
from collections import Counter

STOPWORDS = set('a an and are as at be by for from has have in into is it its of on or our that the their this to with will you your we they experience work role skills required preferred using strong ability knowledge'.split())

def extract_text_from_pdf(uploaded_file):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf with: pip install pypdf") from exc
    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

def _terms(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-/]{1,}", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def _api_key():
    try:
        import streamlit as st
        return st.secrets.get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    except Exception:
        return os.getenv("OPENAI_API_KEY", "")

def _llm_json(system, payload):
    key = _api_key()
    if not key: return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":system},{"role":"user","content":json.dumps(payload,ensure_ascii=False)}],
            response_format={"type":"json_object"}, temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return None

SYSTEM = """You are CareerPilot, an evidence-first career coach. Analyse only the supplied resume and job description. Never invent candidate experience, credentials, numbers, or accomplishments. Distinguish explicit evidence from inference and missing information. Return valid JSON with keys strengths (array of objects with skill,evidence), gaps (array of objects with skill,action), caveats (array of strings), next_steps (array of strings). Keep advice specific and constructive. Do not provide a hiring probability or claim to calculate an ATS score."""

def analyze_resume(resume, job_description, role="Target role"):
    resume, job_description = resume.strip(), job_description.strip()
    if not resume or not job_description: raise ValueError("Resume and job description are both required")
    ai = _llm_json(SYSTEM, {"role":role,"resume":resume[:14000],"job_description":job_description[:12000]})
    job_terms = list(dict.fromkeys(_terms(job_description)))
    resume_lower = resume.lower()
    matched = [t for t in job_terms if t in resume_lower]
    coverage = round(100 * len(matched) / max(1, len(job_terms)))
    if ai:
        strengths = ai.get("strengths", [])[:12]
        gaps = ai.get("gaps", [])[:12]
        caveats = ai.get("caveats", [])[:10]
        next_steps = ai.get("next_steps", [])[:10]
    else:
        strengths = [{"skill":t,"evidence":f"The term '{t}' appears in the supplied resume. Review the relevant line and be ready to explain your contribution."} for t in matched[:8]]
        missing = [t for t in job_terms if t not in resume_lower]
        gaps = [{"skill":t,"action":f"Check whether you have genuine experience with '{t}'. If yes, add a concrete project or experience example; otherwise, learn the basics and build a small demonstrable exercise."} for t in missing[:8]]
        caveats = ["Fallback mode is active: no valid OpenAI API response was available, so the analysis uses keyword matching.","Keyword presence does not prove skill proficiency; validate every match manually.","A missing keyword may reflect different wording rather than a genuine skill gap."]
        next_steps = ["Select three key requirements and identify specific evidence for each.","Rewrite project bullets to describe your action, tools, and measurable result only when accurate.","Build one small demonstrable project for the most important genuine gap.","Practise explaining one project end-to-end, including trade-offs and limitations."]
    report = f"# CareerPilot AI — Role Fit Brief\n\n**Target role:** {role}\n\n**Requirement keyword coverage (heuristic):** {coverage}%\n\n> This is keyword coverage only, not an ATS score or hiring prediction.\n\n## Strengths and evidence\n" + "\n".join(f"- **{x.get('skill','Skill')}** — {x.get('evidence','')}" for x in strengths) + "\n\n## Gaps to investigate\n" + "\n".join(f"- **{x.get('skill','Skill')}** — {x.get('action','')}" for x in gaps) + "\n\n## Reviewer notes\n" + "\n".join(f"- {x}" for x in caveats) + "\n\n## Next steps\n" + "\n".join(f"- {x}" for x in next_steps)
    return {"role":role,"coverage":coverage,"matched_terms":matched,"strengths":strengths,"gaps":gaps,"caveats":caveats,"next_steps":next_steps,"report":report}

def make_interview_pack(role, job, resume, count=8):
    system = "Create a realistic interview practice pack. Ground candidate-specific questions in the supplied resume; do not assume facts not present. Return JSON with questions array of objects: category, question, what_a_strong_answer_covers. Include technical, project, behavioural, and role-specific questions."
    data = _llm_json(system, {"role":role,"job_description":job[:10000],"resume":resume[:10000],"count":count})
    if data and isinstance(data.get("questions"), list):
        return "# Interview Studio — " + role + "\n\n" + "\n\n".join(f"## {i}. {q.get('question','Practice question')}\n**Category:** {q.get('category','General')}\n\n**Strong answer should cover:** {q.get('what_a_strong_answer_covers','Use a real example and explain your reasoning.')}" for i,q in enumerate(data['questions'][:count],1))
    basics = [
        ("Project deep dive", "Choose one project and explain the problem, your contribution, design choices, and result."),
        ("Technical fundamentals", "Explain one core concept required by the role, then give a practical example."),
        ("Debugging", "Describe a difficult bug or failed experiment and the steps you took to isolate it."),
        ("Trade-offs", "What alternative approach did you consider, and why did you choose your solution?"),
        ("Evaluation", "How would you evaluate whether your solution works, and which metrics matter?"),
        ("Behavioural", "Tell me about a time you had to learn something quickly or work through ambiguity."),
        ("Role fit", f"Why are you interested in the {role} role, and which genuine experience best supports that interest?"),
        ("Growth area", "Which skill are you actively improving, and what evidence shows your progress?")]
    return "# Interview Studio — " + role + "\n\n" + "\n\n".join(f"## {i}. {q}\n**Category:** {cat}\n\n**Strong answer should cover:** a clear structure, a specific real example, your own contribution, reasoning, and lessons learned." for i,(cat,q) in enumerate((basics*2)[:count],1))

def make_improvement_plan(analysis=None):
    gaps = [x.get("skill","a priority skill") for x in (analysis or {}).get("gaps",[])[:3]]
    if not gaps: gaps = ["role fundamentals", "project evidence", "interview communication"]
    return [
        {"title":"WEEK 1 · Build the evidence", "tasks":[f"Day 1: Choose one priority requirement — {gaps[0]} — and assess your current level honestly.",f"Day 2–3: Complete a focused tutorial or documentation exercise for {gaps[min(1,len(gaps)-1)]}.","Day 4–5: Build or improve a small project that demonstrates one target-role skill.","Day 6: Add a clear README with setup, design decisions, limitations, and a sample result.","Day 7: Rewrite two resume bullets using accurate actions, tools, and outcomes."]},
        {"title":"WEEK 2 · Prove and practise", "tasks":["Day 8–9: Add tests or evaluation examples to your project and document what they show.","Day 10: Practise a 2-minute explanation of the project and its trade-offs.","Day 11: Solve three role-relevant technical questions and explain your approach aloud.","Day 12: Conduct a mock interview and note unclear or unsupported answers.","Day 13: Tailor the resume to the actual job description without adding unearned skills.","Day 14: Review the application package, GitHub links, README, and interview notes."]}]
