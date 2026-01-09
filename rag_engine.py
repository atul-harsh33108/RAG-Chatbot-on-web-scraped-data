import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Key handling
if "GOOGLE_API_KEY" not in os.environ:
    print("[ERROR] GOOGLE_API_KEY not found in .env")


class RAGEngine:
    def __init__(self, persist_dir="./chroma_db"):
        self.persist_dir = persist_dir
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vectorstore = None
        self.qa_chain = None

    def create_vector_db(self, raw_documents):
        """
        Ingests a list of dicts {'source': url, 'content': text} into ChromaDB.
        """
        print("Processing documents...")
        
        # Convert to LangChain Documents
        docs = [Document(page_content=d['content'], metadata={"source": d['source']}) for d in raw_documents]
        
        # Split text
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)
        print(f"Created {len(splits)} text chunks.")

        # Clean existing DB if needed (optional, here we overwrite or append)
        # For this assignment, let's clear it to be fresh if running locally simply
        if os.path.exists(self.persist_dir):
            try:
                shutil.rmtree(self.persist_dir)
            except:
                pass

        # Create VectorStore with batching to avoid Rate Limits
        print("Embedding and storing in ChromaDB (batched)...")
        import time
        
        # Batch size
        batch_size = 5
        total_chunks = len(splits)
        
        # Initialize chroma with the first batch or empty? 
        # Easier to use Chroma.from_documents for first batch then add_documents
        
        if total_chunks > 0:
            # First batch
            first_batch = splits[:batch_size]
            self.vectorstore = Chroma.from_documents(
                documents=first_batch, 
                embedding=self.embeddings, 
                persist_directory=self.persist_dir
            )
            print(f"Processed 0-{min(batch_size, total_chunks)}/{total_chunks}")
            time.sleep(2) # Wait after first batch
            
            # Remaining batches
            for i in range(batch_size, total_chunks, batch_size):
                batch = splits[i:i + batch_size]
                try:
                    self.vectorstore.add_documents(batch)
                    print(f"Processed {i}-{min(i+batch_size, total_chunks)}/{total_chunks}")
                    time.sleep(2) # 2s delay between batches
                except Exception as e:
                    print(f"Error processing batch {i}: {e}")
                    # Simple retry once
                    time.sleep(10)
                    try:
                         self.vectorstore.add_documents(batch)
                    except:
                        print(f"Failed batch {i} permanently.")

        print("Vector Database created successfully.")

    def load_vector_db(self):
        """Loads existing DB if available"""
        if os.path.exists(self.persist_dir):
            self.vectorstore = Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)
            return True
        return False

    def initialize_chain(self):
        if not self.vectorstore:
            raise ValueError("VectorStore not initialized. Call create_vector_db or load_vector_db first.")

        # Using gemini-flash-latest as verified
        llm = ChatGoogleGenerativeAI(model="models/gemini-flash-latest", temperature=0.3)
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        print("RAG Chain initialized.")

    def query(self, user_query):
        if not self.qa_chain:
            self.initialize_chain()
        
        response = self.qa_chain.invoke({"query": user_query})
        
        answer = response['result']
        source_docs = response.get('source_documents', [])
        
        sources = list(set([doc.metadata.get('source', 'Unknown') for doc in source_docs]))
        
        return answer, sources
