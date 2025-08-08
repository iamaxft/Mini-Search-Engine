import sqlite3
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from collections import defaultdict


class Searcher:
    """
    Loads a pre-built inverted index and allows users to search for queries.
    """

    def __init__(self, db_path, index_path):
        """
        Initializes the Searcher.
        Args:
            db_path (str): The path to the SQLite database file.
            index_path (str): The path to the JSON index file.
        """
        self.db_path = db_path
        self.index_path = index_path
        self.conn = sqlite3.connect(self.db_path)

        # Load the inverted index from the file
        print(f"[*] Loading index from {self.index_path}...")
        with open(self.index_path, 'r') as f:
            self.inverted_index = json.load(f)
        print("[*] Index loaded successfully.")

        # Load English stop words for query processing
        self.stop_words = set(stopwords.words('english'))

    def _preprocess_query(self, query):
        """
        Cleans and tokenizes the user's search query using the same
        method as the indexer.
        """
        query = query.lower()
        query = re.sub(r'[^a-z0-9\s]', '', query)
        tokens = word_tokenize(query)
        return [word for word in tokens if word not in self.stop_words]

    def search(self, query):
        """
        Performs a search for a given query.
        Args:
            query (str): The user's search query.
        Returns:
            A list of tuples, where each tuple contains (url, title_snippet).
        """
        processed_query = self._preprocess_query(query)
        if not processed_query:
            return []

        # Find documents that contain ALL the words in the query
        # Start with the document list for the first word
        try:
            result_doc_ids = set(self.inverted_index.get(processed_query[0], []))
        except IndexError:
            return []

        # Intersect with the document lists for the other words
        for word in processed_query[1:]:
            result_doc_ids.intersection_update(self.inverted_index.get(word, []))

        if not result_doc_ids:
            return []

        # --- Ranking (Simple Term Frequency) ---
        # We will rank documents based on how many of the query terms appear.
        # A more advanced ranking would be TF-IDF, but this is a great start.
        doc_scores = defaultdict(int)
        for doc_id in result_doc_ids:
            for word in processed_query:
                # Our simple score is just a count of matching query terms
                doc_scores[doc_id] += 1

        # Sort documents by score in descending order
        sorted_doc_ids = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)

        # Fetch the URLs and titles for the top results
        results = []
        cursor = self.conn.cursor()
        for doc_id in sorted_doc_ids:
            cursor.execute("SELECT url, text_content FROM pages WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                url, text_content = row
                # Create a simple title snippet from the first 100 chars
                title_snippet = text_content[:100].strip() + "..."
                results.append((url, title_snippet))

        return results

    def start_search_interface(self):
        """Starts a command-line interface for users to enter queries."""
        print("\n--- Mini Search Engine ---")
        print("Type your query and press Enter. Type 'exit' to quit.")
        while True:
            query = input("\n> ")
            if query.lower() == 'exit':
                break

            results = self.search(query)

            if not results:
                print("No results found.")
            else:
                print(f"\nFound {len(results)} results:")
                for i, (url, snippet) in enumerate(results, 1):
                    print(f"{i}. {url}")
                    print(f"   {snippet}\n")

        self.conn.close()
        print("Goodbye!")


# --- Main Execution ---
if __name__ == "__main__":
    db_file = "search_engine.db"
    index_file = "inverted_index.json"

    searcher = Searcher(db_path=db_file, index_path=index_file)
    searcher.start_search_interface()
