import io
import requests
import streamlit as st
import textwrap
from typing import List
from pathlib import Path

# 1 – Backend URL is hardcoded (you can also load via dotenv if needed)
BACKEND_URL = "https://turtil-project.onrender.com"

# 2 – Streamlit page config
st.set_page_config(
    page_title="Turtil Resume ↔︎ Role Fit Evaluator",
    page_icon="🐢",
    layout="centered",
)

st.title("🐢 Turtil – Resume ⇆ Role Fit Evaluator")
st.write(
    "Paste your *resume* and the *job description* below, then click *Evaluate* "
    "to see the fit score, missing skills, and a personalised learning path."
)

# 3 – Utility: extract text from uploaded files (PDF / DOCX)
def _extract_text(file: io.BytesIO, filename: str) -> str:
    try:
        if filename.lower().endswith(".pdf"):
            import fitz  # PyMuPDF
            text = ""
            with fitz.open(stream=file.read(), filetype="pdf") as pdf:
                for page in pdf:
                    text += page.get_text("text")
            return text.strip()

        if filename.lower().endswith(".docx"):
            from docx import Document
            doc = Document(file)
            return "\n".join(para.text for para in doc.paragraphs).strip()
    except Exception as exc:
        st.warning(f"⚠️ Could not read *{filename}* – {type(exc)._name_}: {exc}")
    return ""

# 4 – Sidebar backend tools
with st.sidebar:
    st.header("⚙️ Backend")
    st.write(f"Endpoint: {BACKEND_URL}")

    if st.button("🔎 Ping backend"):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=5)
            r.raise_for_status()
            st.success("Backend is up ✅")
        except Exception as exc:
            st.error(f"Backend not reachable – {exc}")

    st.markdown(f"[View API docs]({BACKEND_URL}/docs)")

# 5 – Input form
with st.form("fit_form", clear_on_submit=False, border=True):
    # Resume input
    st.subheader("1. Resume")
    resume_tab1, resume_tab2 = st.tabs(["📄 Paste text", "📑 Upload PDF / DOCX"])
    resume_text = ""

    with resume_tab1:
        resume_text = st.text_area(
            "Paste the *entire resume text* here ⬇️",
            height=250,
            placeholder="e.g. Experienced Python developer with 5 years…",
            key="resume_text",
        )
    with resume_tab2:
        resume_file = st.file_uploader(
            "Or upload your resume (PDF or DOCX)",
            type=["pdf", "docx"],
            key="resume_file",
        )
        if resume_file is not None:
            resume_text = _extract_text(io.BytesIO(resume_file.read()), resume_file.name)
            if resume_text:
                st.success("Text extracted. You can still edit it in the other tab.")
                resume_tab1.text_area("", resume_text, height=250, key="resume_text_uploaded")

    # JD input
    st.subheader("2. Job Description")
    jd_text = st.text_area(
        "Paste the *job description* here ⬇️",
        height=200,
        placeholder="e.g. We are looking for a Python backend engineer…",
        key="jd_text",
    )

    submitted = st.form_submit_button("🚀 Evaluate 📊")

# 6 – Evaluate & display results
if submitted:
    if not resume_text.strip() or not jd_text.strip():
        st.warning("Please provide *both* resume and job-description text.")
        st.stop()

    with st.spinner("Contacting backend, please wait…"):
        try:
            payload = {"resume_text": resume_text, "job_description": jd_text}
            r = requests.post(f"{BACKEND_URL}/evaluate", json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.JSONDecodeError:
            st.error("Received non-JSON response. Check FastAPI output.")
            st.stop()
        except Exception as exc:
            st.error(f"❌ Backend request failed – {exc}")
            st.stop()

    # Show results
    st.success("Analysis complete!")

    fit_score = data.get("fit_score")
    if fit_score is not None:
        st.metric("🟢 Fit Score", f"{fit_score * 100:.1f}%")

    missing_skills: List[str] = data.get("missing_skills", [])
    if missing_skills:
        st.subheader("🔍 Missing / Weak Skills")
        st.write(", ".join(f"*{skill}*" for skill in missing_skills))

    learning_path = data.get("learning_path", [])
    if learning_path:
        st.subheader("📚 Recommended Learning Path")
        for idx, step in enumerate(learning_path, start=1):
            st.markdown(f"*{idx}.* {textwrap.fill(step, 90)}")

    with st.expander("🛠 Raw backend response"):
        st.json(data)

# 7 – Footer
st.divider()
st.caption(
    "Made with ❤️ and 🐢 by Team Apogee.  "
    "Backend: FastAPI · Frontend: Streamlit."
)
