import streamlit as st
import requests
import re


from transformers import pipeline
from fpdf import FPDF
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# -------------------- SUMMARIZER LOADER --------------------
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# -------------------- PDF GENERATION --------------------
def generate_pdf_with_hf_summary(jobs_by_title):
    job_text = ""
    for title, jobs in jobs_by_title.items():
        job_text += f"{title}:\n"
        for job in jobs:
            job_text += f"- {job['job_title']} at {job['employer_name']} in {job['job_city']}, {job['job_country']}\n"

    summary = summarizer(job_text, max_length=250, min_length=50, do_sample=False)[0]["summary_text"]

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AI Summary of Job Recommendations", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(summary, styles['BodyText']))
    story.append(Spacer(1, 20))

    for title, jobs in jobs_by_title.items():
        story.append(Paragraph(f"Jobs for {title}:", styles['Heading2']))
        story.append(Spacer(1, 6))

        if not jobs:
            story.append(Paragraph("No jobs found for this role.", styles['BodyText']))
        else:
            for job in jobs:
                line = f"• {job['job_title']} at {job['employer_name']} ({job['job_city']}, {job['job_country']})"
                story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Career Path Tool", layout="centered")

if "page" not in st.session_state:
    st.session_state.page = "landing"

def go_to(page):
    st.session_state.page = page
    st.rerun()

# -------------------- API CONFIG --------------------

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

def clean_career_title(title):
    title = re.sub(r'in .*', '', title)
    title = title.replace("Specialist", "").strip()
    return title

JSEARCH_API_KEY = st.secrets["rapidapi_key"]
api_key = st.secrets["openrouter_key"]

def get_job_listings(role):
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    def query_api(query, country="IN"):
        params = {
            "query": query,
            "page": 1,
            "num_pages": 1,
            "country": country
        }
        try:
            res = requests.get(JSEARCH_URL, headers=headers, params=params)
            data = res.json()
            return data.get("data", [])
        except Exception:
            return []

    words = re.findall(r'\w+', role)
    keyword_query = " OR ".join(words[:3]) if len(words) >= 2 else role

    jobs = query_api(role)
    if jobs:
        return jobs[:5]

    jobs = query_api(keyword_query)
    if jobs:
        return jobs[:5]

    jobs = query_api(keyword_query, country="US")
    return jobs[:5] if jobs else []

def query_mistral(prompt):
    
    #OpenRouter key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]


# ------------------------ LANDING PAGE ------------------------
if st.session_state.page == "landing":
    st.set_page_config(page_title="JobGenie | AI Career Coach", layout="wide")
    col1, col2 = st.columns(2)

    with col1:
        st.image("https://media.istockphoto.com/id/480297303/photo/group-of-business-executives-standing-in-a-row.jpg?s=612x612&w=0&k=20&c=AOTRGeGPlDihtEpF7k_izRDXyJrEBIlRwStJ5aTwgOw=", use_container_width=True)


    with col2:
        st.markdown("<h1 style='font-size: 3.5em; font-weight: bold;'>Unlock the future you</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.2em;'>Say hello to <strong>JobGenie</strong>, your AI-powered career coach that helps you discover career paths and job opportunities tailored just for you.</p>", unsafe_allow_html=True)
        st.markdown("### ")

        if st.button("🚀 Get Started", use_container_width=True):
            go_to("main")

        if st.button("🔍 Learn more about JobGenie", use_container_width=True):
          st.info("""
**JobGenie** is your AI-powered career assistant. It helps you:
- 🎯 Get tailored career paths based on your background  
- 🌍 Find job listings in your country  
- 📝 Export insights and job summaries to PDF  

Created by **Megana Subash**  
Version **1.0**
""")



# ------------------------ MAIN PAGE ------------------------
elif st.session_state.page == "main":
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>JobGenie 1.0</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align: center; font-size: 1.2em; margin-bottom: 20px;'>
        Discover career paths tailored to you — absolutely free.<br>
        Unsure where to begin? Let us guide you.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>🎓 Your Background</h3>", unsafe_allow_html=True)

    education = st.selectbox("What is your highest education level?", ["Select", "High School", "Diploma", "Bachelor's", "Master's", "PhD"])
    interests = st.text_input("What are your interests?", placeholder="e.g., technology, design, biology")
    skills = st.text_input("What are your strongest skills?", placeholder="e.g., coding, writing, leadership")
    career_goals = st.text_area("What are your career goals?", placeholder="e.g., I want a meaningful job that allows creativity.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Career Suggestions", use_container_width=True):
            if education == "Select" or not interests.strip() or not skills.strip() or not career_goals.strip():
                st.warning("⚠️ Please fill in all the fields before submitting.")
            else:
                st.success("✅ Profile submitted! Please wait for 2 minutes. Generating suggestions...")

                prompt = f"""Suggest 3 career paths for someone with the following background:
Education: {education}
Interests: {interests}
Skills: {skills}
Career Goals: {career_goals}

Use this format:
1. Career Title
   - Description
   - First Step to Explore It
"""
                with st.spinner("🧠 Thinking..."):
                    result = query_mistral(prompt)

                st.session_state["career_result"] = result

    if "career_result" in st.session_state:
        st.markdown("### 💡 AI-Generated Career Suggestions")
        st.write(st.session_state["career_result"])

        if st.button("🔎 Show Job Recommendations"):
            go_to("jobs")


# ------------------------ JOB PAGE ------------------------
elif st.session_state.page == "jobs":
    st.title("💼 Job Recommendations")

    result = st.session_state.get("career_result", "")
    if not result:
        st.warning("⚠️ No career suggestions found. Please return to the main page and generate suggestions first.")
    else:
        career_titles = re.findall(r'\d+\.\s(.+?)\n', result)
        jobs_by_title = {}

        for title in career_titles:
            clean_title = clean_career_title(title)
            st.markdown(f"#### 📌 Jobs for: **{clean_title}**")
            st.caption(f"Searching with: `{clean_title}`")
            jobs = get_job_listings(clean_title)
            jobs_by_title[clean_title] = jobs

            if jobs:
                for job in jobs:
                    st.write(f"**{job['job_title']}** at *{job['employer_name']}* — {job['job_city']}, {job['job_country']}")
                    st.write(f"[View Job Posting]({job['job_apply_link']})")
                    st.markdown("---")
            else:
                st.write("🔍 No jobs found for this role.")

        st.markdown("### 📄 Export Job Results")
        if st.button("📥 Export as PDF with AI Summary"):
            with st.spinner("Generating summary and formatting PDF..."):
                pdf_bytes = generate_pdf_with_hf_summary(jobs_by_title)
                st.success("✅ PDF ready!")

                st.download_button(
                    label="📄 Download Job Summary PDF",
                    data=pdf_bytes,
                    file_name="job_recommendations.pdf",
                    mime="application/pdf"
                )

    if st.button("⬅️ Back to Career Suggestions"):
        go_to("main")
