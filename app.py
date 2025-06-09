import streamlit as st
import requests

st.set_page_config(page_title="Resume - Role Fit Evaluator")

st.title("📄 Resume - Role Fit Evaluator")

st.markdown("Upload your *resume (PDF)* and paste the *job description* to get your matching track.")

# Upload resume
resume_file = st.file_uploader("📎 Upload your Resume (PDF)", type=["pdf"])

# Job description input
job_description = st.text_area("🧾 Paste Job Description here")

# Submit button
if st.button("🚀 Evaluate Fit"):
    if resume_file and job_description:
        with st.spinner("Sending data to backend..."):
            try:
                response = requests.post(
                    "https://turtil-project.onrender.com/predict",  # Your FastAPI backend
                    files={"resume": resume_file},
                    data={"jd": job_description},
                )
                if response.status_code == 200:
                    st.success("✅ Evaluation complete!")
                    st.json(response.json())
                else:
                    st.error("❌ Backend error. Please check server or try again later.")
            except Exception as e:
                st.error(f"❌ Failed to connect to backend: {e}")
    else:
        st.warning("⚠️ Please upload a resume and paste a job description.")
