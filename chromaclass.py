from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
from chromadb.utils.embedding_functions import EmbeddingFunction
import chromadb


model = SentenceTransformer('paraphrase-albert-small-v2')

class SentenceTransformerEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model):
        self.model = model

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.model.encode(input).tolist()


client_config = {
    'chroma': {
        'client': lambda: chromadb.PersistentClient(),
        'embedding_function': lambda: SentenceTransformerEmbeddingFunction(model)
    }
}





class ChromaObj(ABC):
    @abstractmethod
    def create_collection(self, name: str, metadata: dict): ...
    @abstractmethod
    def add_to_collection(self, param: dict, name: str = None): ...
    @abstractmethod
    def update_to_collection(self, param: dict, name: str = None): ...
    @abstractmethod
    def get_collection(self, name: str): ...
    @abstractmethod
    def delete_from_collection(self, param: dict, name: str = None): ...
    @abstractmethod
    def query_collection(self, param: dict, name: str = None): ...
    @abstractmethod
    def use_collection(self, name: str): ...

class Chroma(ChromaObj):
    """
    Represents a Chroma object for managing data collections, including creation,
    access, modification, and querying.

    The Chroma class provides an interface for organizing data into collections,
    facilitating operations such as adding, updating, deleting, querying, and
    listing collections. It enables users to interact with embedding-based
    functionalities and manage metadata effectively.

    Attributes:
        client: The client object initialized from the provided configuration.
        embedding_function: Reference to the embedding function used in operations.
        collections: A dictionary holding the collections managed by the instance.
        current_collection: The current active collection name.

    Methods:
        create_collection:
            Creates a new collection and stores it within the local instance.
        use_collection:
            Sets the active collection for further operations.
        _get_collection:
            Retrieves a specific collection based on its name.
        add_to_collection:
            Adds documents, metadata, and ID entries to an existing collection.
        update_to_collection:
            Updates documents, metadata, and ID entries in an existing collection.
        get_collection:
            Fetches the reference of a specific collection by its name.
        delete_from_collection:
            Deletes entries from a collection based on IDs or conditions.
        query_collection:
            Queries a collection with specific parameters and retrieves results.
        peek:
            Returns a sample of documents in the specified or active collection.
        count:
            Returns the count of entries in the specified or active collection.
        collection_exist:
            Checks if a collection exists based on its name.
        list_collections:
            Lists all available collections from the client interface.
    """
    def __init__(self, client):
        self.client = client['chroma']['client']()
        self.embedding_function = client['chroma']['embedding_function']()
        self.collections = {}
        self.current_collection = None

    def create_collection(self, name: str, metadata: dict):
        collection = self.client.create_collection(
            name=name,
            embedding_function=self.embedding_function,
            metadata=metadata
        )
        self.collections[name] = collection
        self.current_collection = name

    def use_collection(self, name: str):
        if name in self.collections:
            self.current_collection = name
        else:
            collection = self.client.get_collection(
                name=name,
                embedding_function=self.embedding_function
            )
            self.collections[name] = collection
            self.current_collection = name

    def _get_collection(self, name: str = None):
        name = name or self.current_collection
        if not name:
            raise ValueError("No collection specified or in use.")
        if name not in self.collections:
            raise ValueError(f"Collection '{name}' not found.")
        return self.collections[name]

    def add_to_collection(self, param: dict, name: str = None):
        collection = self._get_collection(name)
        print(param.get('documents'))
        collection.add(
            documents=param.get('documents'),
            metadatas=param.get('metadatas'),
            ids=param.get('ids')
        )

    def update_to_collection(self, param: dict, name: str = None):
        collection = self._get_collection(name)
        collection.update(
            documents=param.get('documents'),
            metadatas=param.get('metadatas'),
            ids=param.get('ids')
        )

    def get_collection(self, name: str):
        return self._get_collection(name)

    def delete_from_collection(self, param: dict, name: str = None):
        collection = self._get_collection(name)
        return collection.delete(
            ids=param.get('ids'),
            where=param.get('where')
        )

    def query_collection(self, param: dict, name: str = None):
        collection = self._get_collection(name)
        return collection.query(
            include=["documents", "metadatas", "distances"],
            query_texts=param.get('query'),
            n_results=param.get('n_results', 1)
        )

    def peek(self,name: str = None):
        collection = self._get_collection(name)
        return collection.peek()

    def count(self,name:str=None):
        collection = self._get_collection(name)
        return collection.count()

    def collection_exist(self,name:str):
        collection_list = self.client.list_collections()
        print(collection_list)
        collection_status = any(col == name for col in collection_list)
        return collection_status
    def list_collections(self):
        collection_list = self.client.list_collections()
        return collection_list