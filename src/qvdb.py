import chromadb
from chromadb.config import Settings
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


class VectorDB:
    """
    A class that represents a vector DB for doing similarity search.

    Attributes:
        db_directory (optional): Directory where to store the DB.
    """

    def __init__(self, db_directory: Optional[str] = "qvdb", collection_name: Optional[str] = "qvdb-collection"):
        
        self.db_directory = db_directory
        self.collection_name = collection_name

        self.client_settings = Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=db_directory,
            allow_reset=True,
        )
        
        self.client = chromadb.Client(settings=self.client_settings)

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"} # l2 is the default
        )

    def add(self, documents: List[str], metadatas: List[dict], ids: List[str]) -> None:
        """
        Add documents to the DB.

        Args:
            documents: List of document strings to add to the DB.
            metadatas: List of metadata dictionaries to add to the DB.
            ids: List of ID strings to add to the DB.
        """
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Query the DB.

        Args:
            query: Query string.
            num_results: Number of results to return.

        Returns:
            List of dictionaries containing the results.
        """
        return self.collection.query(query=query, num_results=num_results)
    
    def similarity_search(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Perform a similarity search on the DB.

        Args:
            query: Query string.
            num_results: Number of results to return.

        Returns:
            List of dictionaries containing the results.
        """
        return self.collection.similarity_search(query=query, num_results=num_results)

    def reset(self):
        """
        Reset the DB.
        """
        self.client.reset() 

