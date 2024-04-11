import json
import requests
import os
from bs4 import BeautifulSoup
from googlesearch import search
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import threading
import time
import itertools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)




class Spinner:
    def __init__(self, message='Loading...'):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.thread = threading.Thread(target=self.spin)
        self.running = False
        self.message = message

    def start(self):
        self.running = True
        self.thread.start()

    def spin(self):
        while self.running:
            print(next(self.spinner), end='\r')
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.thread.join()


def print_verbose(*args) -> None:
    """
    Prints the given arguments if the QAI_VERBOSE environment variable is set.

    Args:
        *args: Variable number of arguments to be printed.

    Returns:
        None
    """
    if os.getenv('QAI_VERBOSE'):
        print(*args)

#
# The yield keyword in Python is used in a function like a return statement,
# but instead of returning a value and terminating the function, yield produces
# a value and suspends the function’s execution. The function can be resumed
# later on from where it left off, allowing it to produce a series of results
# over time, rather than computing them all at once and sending them back like
# a list.
#
# In the context of the extract_json_objects function, each time a JSON object
# is found in the text, it is decoded and then yielded. This means that the function
# produces the JSON objects one at a time and pauses its execution each time it
# yields one. The next time the function is resumed (for example, in the next
# iteration of a loop), it picks up where it left off and finds the next JSON object,
# if there is one.
#
def extract_json_objects(text, decoder=json.JSONDecoder()) -> Iterable[Dict[str, Any]]:
    """Find JSON objects in text, and yield the decoded JSON data

    Args:
        text (str): The text to search for JSON objects.
        decoder (json.JSONDecoder, optional): The JSON decoder to use. Defaults to json.JSONDecoder().

    Yields:
        dict: The decoded JSON data.

    Raises:
        None

    Returns:
        None
    """
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1




class VectorStore:
    """
    A class that represents a vector store for similarity search.

    Attributes:
        db (Chroma): The Chroma database used for storing vectors.
        embedding_model (OllamaEmbeddings): The embedding model used for vectorization.
    """

    def __init__(self, persist_directory: Optional[str] = None):
        
        self.embedding_model = OllamaEmbeddings(model="nomic-embed-text")

        if persist_directory and os.path.isdir(persist_directory):
            self.db = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=persist_directory
                )
        else:
            self.db = None
        

    def search_and_store(self, query: str, num_results: int = 5) -> None:
        """
        Performs a Google Search for documents related to the given query,
        extracts their content, and stores them in the vector store.

        Args:
            query (str): The query to search for documents.
            num_results (int): The number of URLs to retrieve. Defaults to 5.

        Returns:
            None
        """
        documents = []
        metadatas = []
        ids = []
        for index, url in enumerate(search(query, num_results)):
            print_verbose(f"<info> ({index}) Extracting content from: {url}")
            text_splits = self.extract_content(url)
            for jindex, text in enumerate(text_splits):
                documents.append(text)
                metadatas.append({'source': url})
                ids.append(f"id{index}.{jindex}")

        self.store(documents, metadatas, ids)

    def store(self, documents: List[str], metadatas: List[dict], ids: List[str], persist_directory: Optional[str] = None) -> None:
        """
        Store the given documents, metadatas, and ids in the database.

        Args:
            documents (List[str]): The list of documents to store.
            metadatas (List[dict]): The list of metadata dictionaries corresponding to each document.
            ids (List[str]): The list of ids corresponding to each document.

        Returns:
            None
        """
        self.db = Chroma.from_texts(
            documents,
            metadatas=metadatas,
            ids=ids,
            embedding=self.embedding_model,
            persist_directory=persist_directory
        )

    def extract_content(self, url: str) -> List[str]:
        """
        Extracts the content from the given URL.

        Args:
            url (str): The URL to extract content from.

        Returns:
            str: The extracted content.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])  # Extract text from <p> tags

        # We need to split it up into smaller pieces
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_splits = text_splitter.split_text(text)

        return text_splits

    def similarity_search(self, query: str, num_results: int = 1) -> List[Document]:
        """
        Performs a similarity search on the vector store using the given query.

        Args:
            query (str): The query for similarity search.
            num_results (int): The number of results to retrieve. Defaults to 1.

        Returns:
            List[Document]: The similarity search results.
        """
        results = self.db.similarity_search(query=query, k=num_results)
        return results
    
# Example usage
if __name__ == "__main__":
    v = VectorStore()
    query = "Who got the Nobel Prize in Literature in 2023?"
    v.search_and_store(query)
    similar_results = v.similarity_search(query)
    if similar_results:
        print(similar_results[0].page_content)

