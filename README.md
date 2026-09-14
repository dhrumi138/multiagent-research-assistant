# 🔎 Multi-Agent Research Assistant

An AI-powered multi-agent research assistant that automatically searches the web, reads relevant sources, generates a research report, and critiques the final response.

The project combines **LangChain, LangGraph, Tavily, Groq, and Streamlit** to create an end-to-end automated research workflow.

---

## 🚀 Features

- 🔍 **Search Agent** — searches the web for recent and reliable information
- 📖 **Reader Agent** — identifies relevant sources and scrapes deeper content
- ✍️ **Writer Chain** — generates a structured research report
- 🧐 **Critic Chain** — reviews the generated report and provides feedback
- 🎨 **Streamlit UI** — simple interface for running research without using the terminal
- 📄 **Report Download** — download the generated report as a Markdown file
- 🔐 Environment variables for securely storing API keys

---

## 🧠 How It Works

```text
                 Research Topic
                       │
                       ▼
              ┌─────────────────┐
              │   Search Agent  │
              │     🔍          │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Reader Agent  │
              │     📖          │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Writer Chain  │
              │     ✍️          │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Critic Chain  │
              │     🧐          │
              └────────┬────────┘
                       │
                       ▼
                Final Research
                    Report


🛠️ Tech Stack
Python
LangChain
LangGraph
Groq
Tavily
BeautifulSoup
Requests
Streamlit
python-dotenv