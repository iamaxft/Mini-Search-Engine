Mini Search EngineThis project is a complete, functional search engine built from scratch in Python. 
It demonstrates a fundamental understanding of web crawling, data indexing, and information retrieval. 
The system is composed of three core components: a Crawler, an Indexer, and a Searcher.This project serves as a practical example of the core principles 
behind major search engines like Google and showcases key skills in backend software engineering and data structures.
FeaturesWeb Crawler: A polite and robust crawler that navigates websites starting from a seed URL, respects robots.txt protocols,
and stores page content in a local SQLite database.Inverted Indexer: Processes the raw text from crawled pages, cleans it by removing stop words and punctuation, 
and builds an efficient inverted index to map words to the documents they appear in.Ranked Search: A command-line interface that takes user queries, 
uses the inverted index for instant lookups, and ranks the results based on a simple term-frequency scoring algorithm.
Modular Architecture: Cleanly separated components (crawler.py, indexer.py, searcher.py) that demonstrate a well-designed system.
Tech StackLanguage: Python 3Data Storage: SQLite3 (for crawled pages), JSON (for the inverted index)
Core Libraries:requests: For making HTTP requests.BeautifulSoup4: For parsing HTML content.NLTK: For natural language processing tasks like tokenization and
stop word removal.urllib.robotparser: For respecting website crawling rules.Setup and InstallationFollow these steps to get the project running on your local machine.

1. Clone the Repositorygit clone https://github.com/iamaxft/Mini-Search-Engine.git
cd Mini-Search-Engine

2. Create a Virtual EnvironmentIt's highly recommended to use a virtual environment to manage project dependencies.# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Install DependenciesInstall all the required libraries using the requirements.txt file.pip install -r requirements.txt

4. Download NLTK DataThe indexer requires specific data packages from the NLTK library. 

5. Run the following command to download them:python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
UsageThe project must be run in three sequential steps:

Step 1: Run the CrawlerThis will start at the seed URL, crawl up to 50 pages, and save the content in search_engine.db.python crawler.py
Step 2: Run the IndexerThis will read the data from search_engine.db, build the search index, and save it as inverted_index.json.python indexer.py
Step 3: Run the SearcherThis will load the index and start the interactive search interface.python searcher.py

You can now type queries into the terminal. Type exit to quit.