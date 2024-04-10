import json
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


def extract_json_objects(text, decoder=json.JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data
    It's inefficient and error-prone, but it's simple and works for many cases
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
    def __init__(self):
        self.db = None
        self.embedding_model = OllamaEmbeddings(model="nomic-embed-text")

    def search_and_store(self, query: str):
        documents = []
        metadatas = []
        ids = []
        for index,url in enumerate(search(query, num_results=5)):
            text = self.extract_content(url)
            documents.append(text)  
            metadatas.append({'source': url})
            ids.append(f"id{index}")

        self.db = Chroma.from_texts(
            documents,
            metadatas=metadatas,
            ids=ids,
            embedding=self.embedding_model
        )

    def extract_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])  # Extract text from <p> tags
        return text

    def similarity_search(self, query: str, num_results: int = 1):
        results = self.db.similarity_search(query=query, k=num_results)
        return results
    
if __name__ == "__main__":
    v = VectorStore()
    query = "Who got the Nobel Prize in Literature in 2023?"
    v.search_and_store(query)
    similar_results = v.similarity_search(query)
    if similar_results:
        print(similar_results[0].page_content)

