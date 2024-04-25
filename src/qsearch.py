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
import textwrap
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
        for index, url in enumerate(search(query, num_results)):
            print_verbose(f"<info> ({index}) Extracting content from: {url}")
            try:
                text_splits = extract_url_content(url=url)
            except Exception as e:
                print_verbose(f"<error> Failed to extract content from {url}")
                continue

            for jindex, text in enumerate(text_splits):
                qvdb.add(
                    documents=[text],
                    metadatas=[{"source": url}],
                    ids=[f"id{index}.{jindex}"]
                )

def parse_args() -> str:
    parser = argparse.ArgumentParser(description='Search for answer to you question')

    # In this code, nargs='?' means that --pretty can take zero or one argument.
    # If --pretty is present in the command line arguments but no value is provided,
    # args.pretty will be the value of const, which is True in this case.
    # If --pretty is not present, args.pretty will be False because of default=False.
    parser.add_argument('-p', '--pretty', nargs='?', const=72, default=False, help='Print the output within [<N>] characters width (default: 72).')
    parser.add_argument('-q', '--question', type=str, help='Your question')
    parser.add_argument('-v', '--verbose', action='store_true' , help='Output some debug info')

    args = parser.parse_args()

    if not args.question:
        print(f"Error: No question asked. Use --help to see valid input.")
        exit(1)

    if args.verbose:
        os.environ['QSEARCH_VERBOSE'] = 'True'

    return args


if __name__ == '__main__':
        # Parse the command line arguments
        args = parse_args()
        
        # Get the some info from the command line arguments
        question = args.question
        print_pretty = args.pretty

        # Start the spinner
        spinner = Spinner()
        spinner.start()

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
        output = ollama.generate(model=model, system=system, prompt=prompt, stream=False)
        response = output['response'].strip()
        print_verbose(f"Response: {response}")

        # Stop the spinner
        spinner.stop()

        # Print the response
        if print_pretty:
            paragraphs = response.split("\n\n")
            for paragraph in paragraphs:
                wrapped_paragraph = textwrap.fill(paragraph, width=int(print_pretty))
                print(wrapped_paragraph)
                print()
        else:
            print(response)

        # Reset the VectorDB
        qvdb.reset()
