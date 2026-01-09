import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebsiteScraper:
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited = set()
        self.documents = []
        self.domain = urlparse(start_url).netloc

    def is_valid_url(self, url):
        parsed = urlparse(url)
        # Ensure it's the same domain and http/https
        return bool(parsed.netloc == self.domain and parsed.scheme in ['http', 'https'])

    def clean_text(self, text):
        # Basic cleanup: remove extra whitespace
        return " ".join(text.split())

    def crawl(self):
        # Queue stores (url, current_depth)
        queue = [(self.start_url, 0)]
        self.visited.add(self.start_url)

        while queue:
            current_url, depth = queue.pop(0)
            
            if depth > self.max_depth:
                continue

            logging.info(f"Scraping: {current_url} (Depth: {depth})")
            
            try:
                response = requests.get(current_url, timeout=10)
                if response.status_code != 200:
                    logging.warning(f"Failed to fetch {current_url}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract Text Content
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                
                text = self.clean_text(soup.get_text())
                
                if text:
                    self.documents.append({
                        "source": current_url,
                        "content": text
                    })

                # Find links if not at max depth
                if depth < self.max_depth:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(current_url, href)
                        
                        # Remove fragment identifiers
                        full_url = full_url.split('#')[0]

                        if self.is_valid_url(full_url) and full_url not in self.visited:
                            self.visited.add(full_url)
                            queue.append((full_url, depth + 1))
                
                # Politeness sleep
                time.sleep(0.5)

            except Exception as e:
                logging.error(f"Error scraping {current_url}: {e}")

        logging.info(f"Finished crawling. Scraped {len(self.documents)} pages.")
        return self.documents

if __name__ == "__main__":
    scraper = WebsiteScraper("https://botpenguin.com/", max_depth=1)
    docs = scraper.crawl()
    print(f"Sample content from first doc: {docs[0]['content'][:200]}...")
