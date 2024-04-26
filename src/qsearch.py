#
# Created: 25 Apr 2024 by kruskakli@gmail.com
#
import os
import ollama
import argparse
import requests
import itertools
import threading
import time
import functools
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import warnings
from googlesearch import search
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from qvdb import VectorDB
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

# Suppress warnings about insecure HTTPS requests.
warnings.simplefilter('ignore', InsecureRequestWarning)


# Get the value of the environment variable 'USE_MODEL'
# If 'USE_MODEL' is not set or is empty, use a default model instead
model = os.getenv('USE_MODEL', 'llama3')


system="""
You are a helpful AI assistant that helps answer questions based on documents and sources.
You may combine your own knowledge with the information in the documents to answer the questions.
If you make use of the provided documents then add the sources to the answer.

Example of the documents:

SOURCE: https://www.example.com
DOCUMENT: This is an example document.

"""


template = """
Here is the question: {question}

Here are the documents and the corresponding sources:
{documents}

"""


def log_execution_time(func):
    """Decorator to log the execution time of a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        if os.getenv('QSEARCH_RUNTIME'):
            print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result

    return wrapper

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
    if os.getenv('QSEARCH_VERBOSE'):
        print(*args)
        

@log_execution_time
def extract_url_content(url: str) -> List[str]:
        """
        Extracts the content from the given URL.

        Args:
            url (str): The URL to extract content from.

        Returns:
            str: The extracted content.
        """
        response = requests.get(url, verify=False, timeout=4.0)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])  # Extract text from <p> tags

        # We need to split it up into smaller pieces
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_splits = text_splitter.split_text(text)

        return text_splits

@log_execution_time
def google_search(query: str, num_results: int = 5) -> List[str]:
    """
    Performs a Google Search for documents related to the given query.

    Args:
        query (str): The query to search for documents.
        num_results (int): The number of URLs to retrieve. Defaults to 5.

    Returns:
        List[str]: The URLs of the search results.
    """
    return search(query, num_results)


@log_execution_time
def store_documents(qvdb: VectorDB, text_splits: List[str], url: str) -> None:
        """
        Stores the documents in the VectorDB.

        Args:
            qvdb (VectorDB): The VectorDB instance to store the documents in.
            text_splits (List[str]): The list of document text splits.
            url (str): The URL of the source of the documents.

        Returns:
            None
        """
        for index, text in enumerate(text_splits):
            if len(text) > 0:
                qvdb.add(
                    documents=[text],
                    metadatas=[{"source": url}],
                    ids=[f"id-{url}-{index}"]
                )
            


@log_execution_time
def search_and_store(qvdb: VectorDB, query: str, num_results: int = 5) -> None:
        """
        Performs a Google Search for documents related to the given query,
        extracts their content, and stores them in the vector store.

        Args:
            query (str): The query to search for documents.
            num_results (int): The number of URLs to retrieve. Defaults to 5.

        Returns:
            None
        """
        for index, url in enumerate(google_search(query, num_results)):
            print_verbose(f"<info> ({index}) Extracting content from: {url}")
            try:
                text_splits = extract_url_content(url=url)
            except Exception as e:
                print_verbose(f"<error> Failed to extract content from {url}")
                continue
            store_documents(qvdb, text_splits, url)


def parse_args() -> str:
    parser = argparse.ArgumentParser(description='Ask an AI model for answer to you question')

    parser.add_argument('-c', '--chat', action='store_true' , help='Chat mode (i.e not just a single question)')
    parser.add_argument('-t', '--time', action='store_true' , help='Output some runtime info')
    parser.add_argument('-m', '--model', default='llama3', help='Use this Ollama model (default: llama3)')
    parser.add_argument('--persist', nargs='?', const='QAI_DB', default=False, help='Persist/Reuse the VectorDB to/from disk (default: QAI_DB)')
    parser.add_argument('--pdf', type=str, help='PDF files, separated by comma (e.g. file1.pdf,file2.pdf). Requires --rag.')
    parser.add_argument('-q', '--question', type=str, help='Your question')
    parser.add_argument('-r', '--rag', action='store_true' , help='Enable RAG functionality')
    parser.add_argument('-v', '--verbose', action='store_true' , help='Output some debug info')


    args = parser.parse_args()

    if not args.question:
        print(f"Error: No question asked. Use --help to see valid input.")
        exit(1)

    if args.verbose:
        os.environ['QSEARCH_VERBOSE'] = 'True'
    
    if args.time:
        os.environ['QSEARCH_RUNTIME'] = 'True'

    return args


@log_execution_time
def call_ollama(model: str, system: str, prompt: str, stream: bool = False) -> Dict[str, Any]:
    """
    Calls the Ollama model with the given prompt.

    Args:
        model (str): The name of the Ollama model to use.
        system (str): The system text to prepend to the prompt.
        prompt (str): The prompt to send to the Ollama model.
        stream (bool): Whether to stream the response or not.

    Returns:
        Dict[str, Any]: The response from the Ollama model.
    """
    return ollama.generate(model=model, system=system, prompt=prompt, stream=stream)



def main(args):

    if not args.verbose and not args.time:
        # Start the spinner
        spinner = Spinner()
        spinner.start()
    
    # Get the some info from the command line arguments
    question = args.question

    # Create a new VectorDB instance
    qvdb = VectorDB(is_persistent=False)

    # Search for documents related to the question and store them in the VectorDB
    search_and_store(qvdb=qvdb, query=question, num_results=5)
    results = qvdb.query(question, num_results=5)

    # Extract the documents and sources from the results
    docs=[]
    for d, s in zip(results['documents'][0], results['metadatas'][0]):
            docs.append(f"SOURCE: {s['source']}\nDOCUMENT: {d}\n")
    documents = ' '.join(docs)

    # Generate the response
    prompt = template.format(question=question, documents=documents)
    output = call_ollama(model=model, system=system, prompt=prompt, stream=False)
    response = output['response'].strip()
    print_verbose(f"Response: {response}")

    if not args.verbose and not args.time:
        # Stop the spinner
        spinner.stop()

    # Print the response
    print(response)

    # Reset the VectorDB
    qvdb.reset()


if __name__ == '__main__':
        # Parse the command line arguments
        args = parse_args()

        # Call the main function with the parsed arguments
        main(args)
        

