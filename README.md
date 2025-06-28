# 🎯 JobGenie – AI-Powered Career Assistant

JobGenie is a smart career assistant web app built with Streamlit. It helps users discover personalized career paths and job listings using AI.

## 🔍 Features

- 🎓 Suggests career paths based on user background, interests, and goals
- 🤖 Uses **Mistral 7B** (via OpenRouter) to generate personalized career advice
- 🌐 Fetches real-time job listings using the **JSearch API** (RapidAPI)
- 📄 Summarizes job results and exports insights to PDF
- 🚀 Deployed on **Streamlit Cloud** with secure API key handling

## 🛠️ Tech Stack

- **Frontend & App**: Python, Streamlit
- **AI Integration**: Mistral 7B via OpenRouter, Hugging Face Transformers
- **Job Search API**: JSearch (RapidAPI)
- **PDF Generation**: ReportLab
- **Deployment**: Streamlit Cloud
- **Version Control**: Git & GitHub

## 📦 Installation

```bash
git clone https://github.com/meganasubash/jobgenie.git
cd jobgenie
pip install -r requirements.txt
streamlit run jobgenie_app.py

🧠 How It Works
1.Users enter their education, interests, skills, and career goals
2.Mistral 7B returns tailored career suggestions
3.Relevant jobs are fetched via JSearch API
4.Results are summarized and downloadable as a PDF


🙋‍♀️ Creator
Made with 💡 by Megana Subash
