import sqlite3
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import time


class Indexer:
    """
    Reads crawled data from an SQLite database, builds an inverted index,
    and saves it to a JSON file.
    """

    def __init__(self, db_path, index_path):
        """
        Initializes the Indexer.
        Args:
            db_path (str): The path to the SQLite database file.
            index_path (str): The path where the JSON index file will be saved.
        """
        self.db_path = db_path
        self.index_path = index_path
        self.conn = sqlite3.connect(self.db_path)

        # Load English stop words
        self.stop_words = set(stopwords.words('english'))

        # The core data structure for our search engine
        self.inverted_index = {}

    def _preprocess_text(self, text):
        """
        Cleans and tokenizes text.
        1. Converts to lowercase.
        2. Removes non-alphanumeric characters.
        3. Tokenizes into words.
        4. Removes stop words.
        Returns:
            A list of processed words (tokens).
        """
        # Convert to lowercase
        text = text.lower()
        # Remove anything that is not a letter or a number
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Tokenize the text into words
        tokens = word_tokenize(text)
        # Remove stop words
        processed_tokens = [word for word in tokens if word not in self.stop_words]
        return processed_tokens

    def build_index(self):
        """
        Builds the inverted index from the pages in the database.
        The index maps each word to a list of document IDs where it appears.
        """
        print("[*] Starting to build the inverted index...")
        start_time = time.time()

        cursor = self.conn.cursor()
        # Fetch the id and text content of all crawled pages
        cursor.execute("SELECT id, text_content FROM pages")

        rows = cursor.fetchall()
        total_docs = len(rows)
        print(f"[*] Found {total_docs} documents to index.")

        for i, row in enumerate(rows):
            doc_id, text_content = row
            print(f"  -> Processing document {doc_id} ({i + 1}/{total_docs})")

            processed_words = self._preprocess_text(text_content)

            for word in processed_words:
                # If the word is new, add it to the index
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                # Add the document ID to the word's posting list, avoiding duplicates
                if doc_id not in self.inverted_index[word]:
                    self.inverted_index[word].append(doc_id)

        self.conn.close()
        end_time = time.time()
        print(f"\n[*] Indexing complete. Took {end_time - start_time:.2f} seconds.")
        print(f"[*] Total unique words in index: {len(self.inverted_index)}")

    def save_index(self):
        """Saves the inverted index to a JSON file."""
        print(f"[*] Saving index to {self.index_path}...")
        with open(self.index_path, 'w') as f:
            json.dump(self.inverted_index, f, indent=4)
        print("[*] Index saved successfully.")


# --- Main Execution ---
if __name__ == "__main__":
    db_file = "search_engine.db"
    index_file = "inverted_index.json"

    indexer = Indexer(db_path=db_file, index_path=index_file)
    indexer.build_index()
    indexer.save_index()
