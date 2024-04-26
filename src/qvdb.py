import chromadb
from chromadb.utils import embedding_functions
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

# See also: https://realpython.com/chromadb-vector-database/


class VectorDB:
    """
    A class that represents a vector DB for doing similarity search.

    Attributes:
        db_directory (optional): Directory where to store the DB.
        collection_name (optional): Name of the collection.
        embed_model (optional): Name of the sentence transformer model to use for embedding.
    """

    def __init__(self,
                 db_directory: Optional[str] = "qvdb",
                 collection_name: Optional[str] = "qvdb-collection",
                 is_persistent: Optional[bool] = True,
                 embed_model: Optional[str] = None
                 ):
        
        self.db_directory = db_directory
        self.collection_name = collection_name

        # See also: https://www.sbert.net/docs/pretrained_models.html
        self.embed_model = embed_model or "all-MiniLM-L6-v2"
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embed_model
        )

        self.client_settings = Settings(
            anonymized_telemetry=False,
            is_persistent=is_persistent,
            persist_directory=db_directory,
            allow_reset=True,
        )
        
        self.client = chromadb.Client(settings=self.client_settings)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}, # l2 is the default
            embedding_function=self.embedding_func,
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
        return self.collection.query(query_texts=query, n_results=num_results)
    
    def reset(self):
        """
        Reset the DB.
        """
        self.client.reset() 


#
# Test the VectorDB class
#
if __name__ == '__main__':
    qvdb = VectorDB(is_persistent=False)
    # See also: https://www.gutenberg.org/cache/epub/62/pg62.txt
    text = """
    The roof of the enclosure was of solid glass about four or five inches
in thickness, and beneath this were several hundred large eggs,
perfectly round and snowy white. The eggs were nearly uniform in size
being about two and one-half feet in diameter.

Five or six had already hatched and the grotesque caricatures which sat
blinking in the sunlight were enough to cause me to doubt my sanity.
They seemed mostly head, with little scrawny bodies, long necks and six
legs, or, as I afterward learned, two legs and two arms, with an
intermediary pair of limbs which could be used at will either as arms
or legs.

Their eyes were set at the extreme sides of their heads a
trifle above the center and protruded in such a manner that they could
be directed either forward or back and also independently of each
other, thus permitting this queer animal to look in any direction, or
in two directions at once, without the necessity of turning the head.

The ears, which were slightly above the eyes and closer together, were
small, cup-shaped antennae, protruding not more than an inch on these
young specimens. Their noses were but longitudinal slits in the center
of their faces, midway between their mouths and ears.

There was no hair on their bodies, which were of a very light
yellowish-green color. In the adults, as I was to learn quite soon,
this color deepens to an olive green and is darker in the male than in
the female. Further, the heads of the adults are not so out of
proportion to their bodies as in the case of the young.

The iris of the eyes is blood red, as in Albinos, while the pupil is
dark. The eyeball itself is very white, as are the teeth. These latter
add a most ferocious appearance to an otherwise fearsome and terrible
countenance, as the lower tusks curve upward to sharp points which end
about where the eyes of earthly human beings are located.

The whiteness of the teeth is not that of ivory, but of the snowiest
and most gleaming of china. Against the dark background of their olive
skins their tusks stand out in a most striking manner, making these weapons
present a singularly formidable appearance.
"""
    documents = text.split("\n\n")
    for i, doc in enumerate(documents):
        qvdb.add(
            documents=[doc],
            metadatas=[{"paragraph": i}],
            ids=[str(i)]
        )
    query = "What did the creatures look like"
    results = qvdb.query(query, num_results=3)
    print(f"\nQuery: {query}")
    for d, p in zip(results['documents'][0], results['ids'][0]):
        print(f"\nParagraph: {p}\n  {d}\n")
    #print(results)
    qvdb.reset()
