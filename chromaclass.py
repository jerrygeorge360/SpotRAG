from abc import abstractmethod,ABC
from sentence_transformers import SentenceTransformer
import chromadb
client = {
    'chroma':{
    'client': lambda :chromadb.PersistentClient(),
    'embedding_function':lambda : SentenceTransformer('paraphrase-albert-small-v2')
    }
}

class ChromaObj(ABC):
    @abstractmethod
    def create_collection(self,name:str,metadata:dict):
        ...
    @abstractmethod
    def add_to_collection(self,name:str):
        ...
    @abstractmethod
    def update_to_collection(self):
        ...
    @abstractmethod
    def get_collection(self):
        ...
    @abstractmethod
    def delete_collection(self):
        ...
    @abstractmethod
    def query_collection(self):
        ...

class Chroma(ChromaObj):
    def __init__(self,client):
        self.client = client['chroma']['client']
    def create_collection(self,name:str,metadata:dict):
        self.client.create_collection(
            name= name,
            embedding_function = client['chroma']['embedding_function'],
            metadata = metadata
        )
    def add_to_collection(self,name:str):
        ...
    def update_to_collection(self):
        ...
    def get_collection(self):
        ...
    def delete_collection(self):
        ...
    def query_collection