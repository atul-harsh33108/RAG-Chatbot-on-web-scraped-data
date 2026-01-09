import os
import sys
from scraper import WebsiteScraper
from rag_engine import RAGEngine
import logging

# Mute excessively verbose logs from libraries
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

def main():
    print("==================================================")
    print("Welcome to the BotPenguin RAG Chatbot")
    print("==================================================")
    
    rag = RAGEngine()
    
    # Check if we have a vector store or need to scrape
    if not os.path.exists("./chroma_db"):
        print("\n[INFO] No existing index found. Starting scraping content from https://botpenguin.com/ ...")
        print("Note: This might take a few minutes depending on the network and depth.")
        
        # Scrape
        scraper = WebsiteScraper("https://botpenguin.com/", max_depth=2)
        documents = scraper.crawl()
        
        if not documents:
            print("[ERROR] No documents scraped! Exiting.")
            return

        print(f"\n[INFO] Scraped {len(documents)} pages. Creating Vector Database...")
        # Create Index
        rag.create_vector_db(documents)
    else:
        print("\n[INFO] Found existing Vector Database. Loading...")
        rag.load_vector_db()

    print("\n[INFO] Chatbot Initialized! Ready to answer questions.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not query:
                continue

            print("Bot is thinking...", end="\r")
            answer, sources = rag.query(query)
            
            print(f"\rBot: {answer}\n")
            
            if sources:
                print("Sources:")
                for i, src in enumerate(sources, 1):
                    print(f" {i}. {src}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Something went wrong: {e}")

if __name__ == "__main__":
    main()
