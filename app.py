import streamlit as st
from career_engine import analyze_resume, make_interview_pack, make_improvement_plan, extract_text_from_pdf

st.set_page_config(page_title="CareerPilot AI", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --ink:#e9edff; --muted:#a3accb; --panel:#11172a; --line:rgba(167,180,255,.15); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, #222456 0%, #0a0d1a 43%, #080b14 100%); color:var(--ink); }
.block-container { max-width: 1400px; padding-top: 1.7rem; }
[data-testid="stSidebar"] { background:#0b1020; border-right:1px solid var(--line); }
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important; letter-spacing:-.035em;}
.hero {padding:28px 30px; border:1px solid var(--line); border-radius:24px; background:linear-gradient(125deg,rgba(111,84,255,.2),rgba(35,201,220,.07) 70%),#101528; margin-bottom:22px;}
.eyebrow {font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:#a6a9ff;font-weight:700;}
.hero h1 {font-size:40px;line-height:1.08;margin:10px 0 12px;color:#f6f7ff;}
.hero p {color:#b6bfdc;max-width:720px;font-size:15px;}
.panel {padding:20px;border:1px solid var(--line);border-radius:18px;background:rgba(17,23,42,.88);margin-bottom:14px;}
.metric {padding:18px;border:1px solid var(--line);border-radius:16px;background:linear-gradient(140deg,rgba(123,97,255,.13),rgba(18,26,47,.9));}
.metric .num {font-size:28px;font-weight:700;font-family:'Space Grotesk';color:#f7f7ff;}
.metric .lbl {font-size:12px;color:#a7b1d0;margin-top:4px;}
.tag {display:inline-block;border:1px solid rgba(124,224,220,.28);background:rgba(36,190,190,.08);color:#8fe8dc;padding:4px 9px;border-radius:99px;font-size:11px;margin:2px;}
div.stButton>button, div.stDownloadButton>button {border-radius:12px;border:1px solid rgba(151,139,255,.55);background:linear-gradient(100deg,#6e58ee,#4b7de8);color:white;font-weight:700;padding:.62rem 1rem;}
.stTextArea textarea,.stTextInput input {background:#0d1325!important;color:#edf0ff!important;border:1px solid var(--line)!important;border-radius:12px!important;}
.stTabs [data-baseweb="tab-list"] {gap:8px;background:transparent;}
.stTabs [data-baseweb="tab"] {background:#12182b;border:1px solid var(--line);border-radius:10px;padding:8px 16px;}
small,.muted {color:var(--muted);}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ✦ CareerPilot **AI**")
    st.caption("CAREER INTELLIGENCE WORKSPACE")
    page = st.radio("WORKSPACE", ["Resume Lab", "Interview Studio", "Action Plan", "About & Setup"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Your copilot stack**")
    for name, desc in [("01 · Role Strategist", "Maps role requirements"),("02 · Evidence Analyst", "Finds proof in your resume"),("03 · Evidence Reviewer", "Flags gaps & assumptions")]:
        st.markdown(f"<div style='padding:10px 0;border-bottom:1px solid rgba(167,180,255,.1)'><b style='font-size:13px'>{name}</b><br><span style='font-size:11px;color:#a3accb'>{desc}</span></div>", unsafe_allow_html=True)
    st.divider()
    st.caption("Your documents stay in this session. Add an API key in .streamlit/secrets.toml to enable live LLM analysis.")

st.markdown("<div class='hero'><div class='eyebrow'>✦ Your personal AI career command centre</div><h1>Turn your experience<br>into your next opportunity.</h1><p>Understand role fit, surface evidence, close skill gaps, and prepare for interviews — with an evidence-first AI workflow built for real job applications.</p><span class='tag'>Multi-agent workflow</span><span class='tag'>Evidence-first analysis</span><span class='tag'>Interview-ready outputs</span></div>", unsafe_allow_html=True)

if "resume_text" not in st.session_state: st.session_state.resume_text = ""
if "job_text" not in st.session_state: st.session_state.job_text = ""
if "analysis" not in st.session_state: st.session_state.analysis = None

if page == "Resume Lab":
    st.subheader("Resume intelligence")
    st.caption("Add a resume and a target job description. CareerPilot separates evidence you have from skills you may need to develop.")
    left,right = st.columns([.95,1.05], gap="large")
    with left:
        st.markdown("<div class='panel'><b>01 / Your profile</b><p class='muted'>Paste your resume or upload a PDF.</p></div>", unsafe_allow_html=True)
        upload = st.file_uploader("Upload resume (PDF or TXT)", type=["pdf","txt"])
        if upload:
            try:
                st.session_state.resume_text = extract_text_from_pdf(upload) if upload.name.lower().endswith('.pdf') else upload.getvalue().decode('utf-8',errors='ignore')
                st.success(f"Loaded {upload.name}")
            except Exception as e: st.error(f"Could not read file: {e}")
        st.session_state.resume_text = st.text_area("Resume text", value=st.session_state.resume_text, height=270, placeholder="Paste education, skills, projects, internships, achievements...")
    with right:
        st.markdown("<div class='panel'><b>02 / Target role</b><p class='muted'>Use a real job description for a specific analysis.</p></div>", unsafe_allow_html=True)
        role = st.text_input("Target role", placeholder="e.g. Junior AI / ML Engineer")
        st.session_state.job_text = st.text_area("Job description", value=st.session_state.job_text, height=320, placeholder="Paste responsibilities, requirements, and preferred qualifications...")
    if st.button("✦ Run career analysis", type="primary", use_container_width=True):
        if not st.session_state.resume_text.strip() or not st.session_state.job_text.strip(): st.warning("Please provide both resume text and a job description.")
        else:
            with st.spinner("Running role strategist, evidence analyst, and reviewer..."):
                st.session_state.analysis = analyze_resume(st.session_state.resume_text, st.session_state.job_text, role or "Target role")
    result = st.session_state.analysis
    if result:
        st.divider(); st.subheader("Your role-fit brief")
        m1,m2,m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric'><div class='num'>{result['coverage']}%</div><div class='lbl'>Requirement keyword coverage · heuristic</div></div>",unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric'><div class='num'>{len(result['strengths'])}</div><div class='lbl'>Evidence-backed strengths</div></div>",unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric'><div class='num'>{len(result['gaps'])}</div><div class='lbl'>Gaps to investigate</div></div>",unsafe_allow_html=True)
        a,b,c = st.tabs(["Strengths & evidence", "Skill gaps", "Reviewer notes"])
        with a:
            for item in result['strengths']: st.markdown(f"- **{item['skill']}** — {item['evidence']}")
        with b:
            for item in result['gaps']: st.markdown(f"- **{item['skill']}** — {item['action']}")
        with c:
            for note in result['caveats']: st.markdown(f"- {note}")
        st.markdown("#### Suggested next steps")
        for i,step in enumerate(result['next_steps'],1): st.markdown(f"**{i}.** {step}")
        st.download_button("Download analysis (Markdown)", data=result['report'], file_name="careerpilot_analysis.md", mime="text/markdown")

elif page == "Interview Studio":
    st.subheader("Interview Studio")
    st.caption("Generate a role-specific question pack grounded in the job description and your actual experience.")
    role = st.text_input("Role to prepare for", placeholder="AI / ML Engineer")
    job = st.text_area("Job description", value=st.session_state.job_text, height=180, placeholder="Paste the job description")
    resume = st.text_area("Your resume / projects", value=st.session_state.resume_text, height=180, placeholder="Paste the relevant resume sections")
    count = st.slider("Questions", 5, 15, 8)
    if st.button("Generate interview pack", use_container_width=True):
        with st.spinner("Building your interview practice pack..."):
            st.session_state.interview_pack = make_interview_pack(role or "Target role", job, resume, count)
    if st.session_state.get("interview_pack"):
        st.markdown(st.session_state.interview_pack)
        st.download_button("Download question pack", st.session_state.interview_pack, "careerpilot_interview_pack.md", "text/markdown")

elif page == "Action Plan":
    st.subheader("Your 14-day improvement sprint")
    st.caption("A focused plan that turns the analysis into manageable actions. Adjust it to your schedule and verify requirements against the actual job posting.")
    result = st.session_state.analysis
    if result:
        plan = make_improvement_plan(result)
    else:
        plan = make_improvement_plan(None)
        st.info("Run Resume Lab first to personalise this plan. A starter plan is shown meanwhile.")
    for week in plan:
        st.markdown(f"### {week['title']}")
        for task in week['tasks']:
            st.checkbox(task, key="plan_"+str(abs(hash(task))))
    st.download_button("Download action plan", "# CareerPilot AI — 14-day action plan\n\n"+"\n".join(f"## {w['title']}\n"+"\n".join(f"- [ ] {t}" for t in w['tasks']) for w in plan), "careerpilot_action_plan.md", "text/markdown")

else:
    st.subheader("About this project")
    st.markdown("""
    <div class='panel'><h3>Built to show applied AI engineering</h3><p class='muted'>CareerPilot demonstrates prompt design, multi-stage orchestration, structured output validation, document parsing, deterministic fallback behaviour, testable business logic, and an interface for a real workflow.</p></div>
    **Architecture**
    1. **Input layer:** resume PDF/TXT + target job description.
    2. **Role Strategist:** identifies requirements and priorities.
    3. **Evidence Analyst:** maps requirements to resume evidence.
    4. **Evidence Reviewer:** flags unsupported assumptions and missing proof.
    5. **Output layer:** analysis, interview pack, and action plan.

    **Important:** the coverage percentage is a simple keyword heuristic, not an ATS score, hiring probability, or guarantee of selection. AI-generated guidance can be wrong; verify all claims and never add experience you do not have.

    **Setup**
    ```bash
    python -m venv .venv
    # Windows: .venv\\Scripts\\activate
    pip install -r requirements.txt
    streamlit run app.py
    ```
    To enable OpenAI API analysis, add `OPENAI_API_KEY` to `.streamlit/secrets.toml` or your environment. Never commit secrets to GitHub.
    """, unsafe_allow_html=True)
