import streamlit as st
from src.helper import extract_text_from_pdf, extract_keywords, analyze_resume
from src.job_api import fetch_rss_jobs

st.set_page_config(page_title="Job Recommender", layout="wide")
st.title("📄AI Job Recommender")
st.markdown("Upload your resume and get job recommendations based on your skills and experience from LinkedIn and Naukri.")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    with st.spinner("Analyzing your resume..."):
        summary, gaps, roadmap = analyze_resume(resume_text)
    
    # Display nicely formatted results
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{summary}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{gaps}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.markdown(f"<div style='background-color: #000000; padding: 15px; border-radius: 10px; font-size:16px; color:white;'>{roadmap}</div>", unsafe_allow_html=True)

    st.success("✅ Analysis Completed Successfully!")


    if st.button("🔎Get Job Recommendations"):
        with st.spinner("Fetching job recommendations..."):
            keywords, _ = extract_keywords(summary, limit=12)

            search_keywords_clean = keywords.replace("\n", "").strip()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        with st.spinner("Fetching jobs from RSS feeds..."):
            rss_jobs = fetch_rss_jobs(search_keywords_clean, rows=60)


        st.markdown("---")
        st.header("💼 Jobs from RSS feeds")

        if rss_jobs:
            for job in rss_jobs:
                st.markdown(f"**{job.get('title')}** at *{job.get('companyName')}* ({job.get('source')})")
                if job.get('location'):
                    st.markdown(f"- 📍 {job.get('location')}")
                st.markdown(f"- 🔗 [View Job]({job.get('url')})")
                st.markdown("---")
        else:
            st.warning("No jobs found in RSS feeds.")


