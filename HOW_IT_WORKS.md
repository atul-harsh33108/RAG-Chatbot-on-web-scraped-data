# 🧠 How It Works: BotPenguin RAG Chatbot

This document explains the technical architecture and logic behind the chatbot.

## 1. The Concept: RAG (Retrieval-Augmented Generation)
Standard LLMs (like ChatGPT or Gemini) don't know about specific private data or the most recent content of a website. **RAG** bridges this gap by:
1.  **Retrieving** relevant information from a custom knowledge base (our scraped data).
2.  **Augmenting** the prompt to the AI with this information.
3.  **Generating** an answer based strictly on that context.

---

## 2. Step-by-Step Architecture

### Phase A: Data Ingestion (The Scraper)
*   **Script**: `scraper.py`
*   **Logic**:
    1.  **Crawler**: Starts at the homepage (`https://botpenguin.com/`).
    2.  **Traversal**: Uses **Breadth-First Search (BFS)** with a depth limit of 2. This ensures we get the main pages and their immediate sub-pages without crawling the entire internet.
    3.  **Filtering**: It checks every link to ensure it belongs to the `botpenguin.com` domain. External links (Facebook, LinkedIn, etc.) are ignored.
    4.  **Cleaning**: `BeautifulSoup` removes HTML tags, scripts, and navigation bars to extract clean, readable text.

### Phase B: Indexing (The "Brain")
*   **Script**: `rag_engine.py`
*   **Chunking**: Raw text is too long for an AI to read all at once. We split the text into **chunks** of 1,000 characters with a 200-character overlap (to preserve context across splits).
*   **Embedding**: Each chunk is passed to Google's `embedding-001` model. This turns text into a "vector" (a list of numbers representing meaning).
    *   *Example*: "Pricing" and "Cost" will have similar vector numbers.
*   **Storage**: These vectors are stored in **ChromaDB**, a local vector database, located in the `chroma_db/` folder.
    *   *Rate Limiting*: We ingest data in small batches (5 item) with sleep intervals to respect the Gemini API Free Tier limits.

### Phase C: The Retrieval Loop (The Chat)
*   **Script**: `main.py`
*   **Flow**:
    1.  **User Input**: You ask, *"Does it support WhatsApp?"*
    2.  **Search**: The system converts your question into a vector and finds the 3 most similar text chunks in `ChromaDB`.
    3.  **Prompt Engineering**: It constructs a hidden prompt to the AI:
        > "You are a helpful assistant. Use the following pieces of context to answer the question at the end. If you don't know the answer, say you don't know. \n\n Context: [Chunk 1] [Chunk 2] [Chunk 3] \n\n Question: Does it support WhatsApp?"
    4.  **Generation**: Google Gemini (`gemini-flash-latest`) generates the text response.
    5.  **Citation**: The bot extracts the `source` metadata from the chunks and prints the URLs.

---

## 3. Key Components & Decisions

| Component | Choice | Reason |
| :--- | :--- | :--- |
| **LLM** | `gemini-flash-latest` | Faster and higher rate limits than `gemini-pro`. |
| **Database** | `ChromaDB` | Simple, runs locally (no server setup needed). |
| **Orchestration** | `LangChain` | Handles the complex logic of connecting the database to the LLM. |
| **Config** | `.env` | Keeps your API Key secure and out of the code. |
