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
            query_texts=param.get('query'),
            n_results=param.get('n_results', 5)
        )

    def peek(self,name: str = None):
        collection = self._get_collection(name)
        return collection.peek()

    def count(self,name:str=None):
        collection = self._get_collection(name)
        return collection.count()

    def collection_exist(self,name:str):
        collection_list = self.client.list_collections()
        collection_status = any(col == name for col in collection_list)
        return collection_status