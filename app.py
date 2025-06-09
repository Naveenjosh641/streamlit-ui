import streamlit as st
import requests

# Backend URL deployed on Render
BACKEND_URL = "https://turtil-project.onrender.com"

# Streamlit app UI
st.set_page_config(page_title="Resume Fit Evaluator", layout="wide")

st.title("🎯 Resume–Role Fit Evaluator")

st.markdown("""
This tool checks how well your resume matches a job role and recommends learning steps if needed.
""")

# Input form
with st.form("input_form"):
    resume_text = st.text_area("📄 Paste your Resume Text", height=200)
    job_description = st.text_area("💼 Paste the Job Description", height=200)
    submitted = st.form_submit_button("Evaluate Fit")

# When the form is submitted
if submitted:
    if not resume_text or not job_description:
        st.warning("Please provide both resume text and job description.")
    else:
        with st.spinner("Evaluating..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/evaluate-fit",
                    json={"resume_text": resume_text, "job_description": job_description}
                )
                result = response.json()

                # Show results
                st.success("✅ Evaluation Complete!")

                st.subheader("📊 Fit Score")
                st.metric("Fit Score", f"{result.get('fit_score', 0):.2f}")
                st.write("Verdict:", result.get("verdict", "N/A"))

                st.subheader("✅ Matched Skills")
                matched = result.get("matched_skills", [])
                st.write(", ".join(matched) if matched else "None")

                st.subheader("❌ Missing Skills")
                missing = result.get("missing_skills", [])
                st.write(", ".join(missing) if missing else "None")

                st.subheader("📚 Recommended Learning Track")
                learning_tracks = result.get("recommended_learning_track", [])
                for track in learning_tracks:
                    st.markdown(f"*{track['skill']}*")
                    for i, step in enumerate(track["steps"], 1):
                        st.markdown(f"- Step {i}: {step}")

            except Exception as e:
                st.error("⚠️ Error while contacting the backend.")
                st.exception(e)
