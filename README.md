# 🐧 BotPenguin RAG Chatbot

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-v0.3.0-green?logo=chainlink&logoColor=white)
![Gemini API](https://img.shields.io/badge/AI-Google_Gemini-orange?logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-purple)

A console-based **Retrieval-Augmented Generation (RAG)** chatbot that intelligently answers questions by crawling and indexing content from [BotPenguin.com](https://botpenguin.com/).

This project demonstrates how to build a custom knowledge-base chatbot using **Google's Gemini Pro/Flash models** and **LangChain**.

---

## 🚀 Features

*   **🕷️ Automated Web Scraping**: Custom crawler extracts text content from the target website (depth-limited BFS).
*   **🧠 RAG Architecture**: Retrieval-Augmented Generation pipeline to ground answers in actual website data.
*   **🔗 Citations**: Every answer includes links to the source web pages used for the context.
*   **🔋 Batch Processing**: optimized ingestion to respect Gemini API Free Tier rate limits (`429` handling).
*   **💾 Persistent Memory**: Uses ChromaDB to save the vector index locally, avoiding re-scraping on every run.

---

## 🛠️ Tech Stack

*   **Language**: Python 3.12+
*   **LLM**: Google Gemini (`gemini-flash-latest` / `gemini-pro`)
*   **Embeddings**: Gemini Embeddings (`models/embedding-001`)
*   **Framework**: LangChain, LangChain Community
*   **Vector Store**: ChromaDB
*   **Tools**: BeautifulSoup4 (Scraping), Dotenv (Config)

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd Chatbot_ona_site
```

### 2. Set Up Virtual Environment
It's recommended to use a virtual environment.
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the project root and add your Google Gemini API Key.
```env
# .env file
GOOGLE_API_KEY=AIzaSy...YourKeyHere
```
> **Note**: You can get a free API key from [Google AI Studio](https://aistudio.google.com/).

---

## 🎮 How to Run

Run the main application script:

```bash
python main.py
```

### What Happens Next?
1.  **Check Index**: The bot checks for an existing `chroma_db` folder.
2.  **Scrape (First Run)**: If no index exists, it starts crawling `https://botpenguin.com/` (Depth: 2).
    *   *Note: This may take ~1 minute.*
3.  **Index**: It processes the text into chunks and creates embeddings in batches.
4.  **Chat**: Once ready, the console prompt appears.

**Example Interaction:**
```text
You: What is BotPenguin?
Bot: BotPenguin is an AI-powered chatbot platform that helps businesses automate customer support...
Sources:
 1. https://botpenguin.com/
 2. https://botpenguin.com/features
```

Type `exit` or `quit` to close the application.

---

## 📂 Project Structure

```text
├── main.py : Entry point (CLI interface)
├── rag_engine.py : RAG logic, ChromaDB management, and LangChain setup
├── scraper.py : Web crawler logic using Requests & BeautifulSoup
├── requirements.txt : Python dependencies
├── .env : Configuration file (API Keys)
└── chroma_db/ : (Generated) Local vector database storage
```

---

## ⚠️ Troubleshooting

*   **429 Resource Exhausted**: If you see this during indexing, it means the API rate limit was hit. The script handles this by waiting and retrying, but initial embedding might be slow on the free tier.
*   **ModuleNotFoundError**: Ensure you activated the virtual environment before running the script.

---
*Created for the BotPenguin Assignment by [Your Name]*
