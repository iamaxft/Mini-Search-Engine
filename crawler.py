import requests
from bs4 import BeautifulSoup
import sqlite3
from collections import deque
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time


class Crawler:
    """
    A web crawler that navigates websites, respects robots.txt,
    and stores page content in an SQLite database.
    """

    def __init__(self, db_path, seed_urls):
        """
        Initializes the Crawler.
        Args:
            db_path (str): The path to the SQLite database file.
            seed_urls (list): A list of starting URLs.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_database()

        # Data structures for crawling
        self.queue = deque(seed_urls)
        self.visited_urls = set()
        self.robot_parsers = {}  # Cache for robot.txt parsers

    def _create_database(self):
        """Creates the database table if it doesn't already exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                html_content TEXT NOT NULL,
                text_content TEXT NOT NULL,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def _can_fetch(self, url):
        """
        Checks if the crawler is allowed to fetch a URL based on robots.txt.
        """
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = urljoin(base_url, "/robots.txt")

        # Check if we have a parser for this site already
        if base_url not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robot_parsers[base_url] = rp
            except Exception as e:
                print(f"Could not read robots.txt for {base_url}: {e}")
                return False  # Behave cautiously if robots.txt is unreadable

        return self.robot_parsers[base_url].can_fetch("*", url)

    def _store_page(self, url, html_content, text_content):
        """Saves a webpage's content to the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pages (url, html_content, text_content)
                VALUES (?, ?, ?)
            ''', (url, html_content, text_content))
            self.conn.commit()
            print(f"  [+] Stored: {url}")
        except sqlite3.IntegrityError:
            # This can happen if two different URLs redirect to the same page
            print(f"  [!] URL already exists: {url}")

    def crawl(self, max_pages=50):
        """
        Starts the crawling process.
        Args:
            max_pages (int): The maximum number of pages to crawl.
        """
        pages_crawled = 0
        while self.queue and pages_crawled < max_pages:
            url = self.queue.popleft()

            if url in self.visited_urls:
                continue

            if not self._can_fetch(url):
                print(f"  [-] Disallowed by robots.txt: {url}")
                continue

            self.visited_urls.add(url)
            print(f"[*] Crawling ({pages_crawled + 1}/{max_pages}): {url}")

            try:
                # Be a polite crawler
                time.sleep(1)
                response = requests.get(url, timeout=5, headers={'User-Agent': 'MiniSearchEngineBot/1.0'})

                if response.status_code != 200:
                    continue

                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract clean text
                text_content = soup.get_text(separator=' ', strip=True)

                # Store the page
                self._store_page(url, html_content, text_content)
                pages_crawled += 1

                # Find and enqueue new links
                for link in soup.find_all('a', href=True):
                    absolute_link = urljoin(url, link['href'])
                    # Basic validation to ensure we are crawling HTTP/HTTPS links
                    if absolute_link.startswith('http'):
                        self.queue.append(absolute_link)

            except requests.RequestException as e:
                print(f"  [!] Error fetching {url}: {e}")
            except Exception as e:
                print(f"  [!] An unexpected error occurred: {e}")

        print("\nCrawling finished.")
        self.conn.close()


# --- Main Execution ---
if __name__ == "__main__":
    # We will use a website designed for scraping as our starting point.
    # Wikipedia is too large; this is a safe and structured choice.
    seed_urls = ["http://quotes.toscrape.com/"]
    db_file = "search_engine.db"

    crawler = Crawler(db_path=db_file, seed_urls=seed_urls)
    crawler.crawl(max_pages=50)

