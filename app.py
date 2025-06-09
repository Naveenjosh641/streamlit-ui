import streamlit as st
import requests

# Set your deployed backend URL here
BACKEND_URL = "https://turtil-project.onrender.com"

st.set_page_config(page_title="Resume–Role Fit Evaluator", layout="wide")
st.title("🎯 Resume–Role Fit Evaluator")
st.markdown("Check how well your resume matches a job role and get learning suggestions.")

# Input form
with st.form("evaluation_form"):
    resume_text = st.text_area("📄 Paste your Resume Text", height=200)
    job_description = st.text_area("💼 Paste the Job Description", height=200)
    submitted = st.form_submit_button("Evaluate Fit")

if submitted:
    if not resume_text or not job_description:
        st.warning("⚠️ Please fill in both fields before submitting.")
    else:
        try:
            with st.spinner("Evaluating resume..."):
                response = requests.post(
                    f"{BACKEND_URL}/evaluate-fit",
                    json={"resume_text": resume_text, "job_description": job_description}
                )

                # Check HTTP status code
                if response.status_code != 200:
                    st.error(f"Backend error: {response.status_code}")
                    st.text(response.text)
                else:
                    result = response.json()

                    st.success("✅ Evaluation Complete!")

                    st.subheader("📊 Fit Score")
                    st.metric("Score", f"{result.get('fit_score', 0):.2f}")
                    st.markdown(f"*Verdict*: {result.get('verdict', 'N/A')}")

                    st.subheader("✅ Matched Skills")
                    matched = result.get("matched_skills", [])
                    st.write(", ".join(matched) if matched else "No matched skills.")

                    st.subheader("❌ Missing Skills")
                    missing = result.get("missing_skills", [])
                    st.write(", ".join(missing) if missing else "No missing skills.")

                    st.subheader("📚 Recommended Learning Tracks")
                    learning_tracks = result.get("recommended_learning_track", [])
                    if learning_tracks:
                        for track in learning_tracks:
                            st.markdown(f"### {track['skill']}")
                            for i, step in enumerate(track["steps"], 1):
                                st.markdown(f"- Step {i}: {step}")
                    else:
                        st.write("🎉 No additional learning needed!")
        except requests.exceptions.RequestException as e:
            st.error("⚠️ Failed to contact the backend.")
            st.text(str(e))
        except ValueError as ve:
            st.error("⚠️ Invalid response from the backend.")
            st.text(str(ve))
