import os
import google.generativeai as genai
import time

import os
import google.generativeai as genai
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def check_api():
    print(f"Configuring Gemini with Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    genai.configure(api_key=API_KEY)
    
    found_gen_model = None
    found_embed_model = None

    print("\n1. Listing Available Models...")
    try:
        for m in genai.list_models():
            print(f"  - {m.name} | Methods: {m.supported_generation_methods}")
            if 'generateContent' in m.supported_generation_methods:
                # Prefer 1.5-flash or pro-latest
                if 'gemini-1.5-flash' in m.name:
                    found_gen_model = m.name
                elif 'gemini-pro' in m.name and found_gen_model is None:
                     found_gen_model = m.name
            
            if 'embedContent' in m.supported_generation_methods:
                if 'embedding-001' in m.name: # Default Preference
                    found_embed_model = m.name
    except Exception as e:
        print(f"  [ERROR] Listing models failed: {e}")
        return

    print(f"\nSelected Generation Model: {found_gen_model}")
    print(f"Selected Embedding Model: {found_embed_model}")

    if found_gen_model:
        print(f"\n2. Testing Generation ({found_gen_model})...")
        try:
            model = genai.GenerativeModel(found_gen_model)
            response = model.generate_content("Hello, can you hear me?")
            print(f"  [SUCCESS] Response: {response.text}")
        except Exception as e:
            print(f"  [ERROR] Generation failed: {e}")
    else:
        print("  [ERROR] No suitable generation model found.")

    if found_embed_model:
        print(f"\n3. Testing Embeddings ({found_embed_model})...")
        try:
            # Retry logic for 429
            max_retries = 3
            for i in range(max_retries):
                try:
                    result = genai.embed_content(
                        model=found_embed_model,
                        content="This is a test sentence.",
                        task_type="retrieval_document",
                        title="Test Document"
                    )
                    print(f"  [SUCCESS] Generated embedding of length: {len(result['embedding'])}")
                    break
                except Exception as e:
                    if "429" in str(e) and i < max_retries - 1:
                        print(f"  [WARNING] Rate limit hit. Retrying in 5 seconds... (Attempt {i+1}/{max_retries})")
                        time.sleep(5)
                    else:
                        raise e
                    
        except Exception as e:
            print(f"  [ERROR] Embedding failed: {e}")
    else:
        print("  [ERROR] No suitable embedding model found.")

if __name__ == "__main__":
    check_api()
