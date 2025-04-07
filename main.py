# install chroma
import chromadb
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("paraphrase-albert-small-v2")
client = chromadb.PersistentClient()


# Sample sentences
sentences = [{'jerry':"I am building a RAG system."}, {"henry":"This is another sentence."}, {"runtime":"Embedding systems are fun!"}]

embedding = model.encode(sentences)


collection = client.create_collection("sentence_embeddings")
for i, sentence in enumerate(sentences):
    collection.add([str(i)], embedding[i], metadatas=[{"text": sentence}])

# Create a collection
collection = client.create_collection(
    name="my_collection",
    embedding_function=emb_fn,
    metadata={
        "description": "my first Chroma collection",
        "created": str(datetime.now())
    }
)

collection = client.get_collection(name="test") # Get a collection object from an existing collection, by name. Will raise an exception if it's not found.
collection = client.get_or_create_collection(name="test") # Get a collection object from an existing collection, by name. If it doesn't exist, create it.
client.delete_collection(name="my_collection") # Delete a collection and all associated embeddings, documents, and metadata. ⚠️ This is destructive and not reversible

collection.peek()
collection.count()
collection.modify(name="new_name")

collection.add(
    documents=["lorem ipsum...", "doc2", "doc3", ...],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    ids=["id1", "id2", "id3", ...]
)

collection.add(
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], ...],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    ids=["id1", "id2", "id3", ...]
)

collection.update(
    ids=["id1", "id2", "id3", ...],
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], ...],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    documents=["doc1", "doc2", "doc3", ...],
)

collection.upsert(
    ids=["id1", "id2", "id3", ...],
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2], ...],
    metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
    documents=["doc1", "doc2", "doc3", ...],
)

collection.delete(
    ids=["id1", "id2", "id3",...],
	where={"chapter": "20"}
)

collection.query(
    query_embeddings=[[11.1, 12.1, 13.1],[1.1, 2.3, 3.2], ...],
    n_results=10,
    where={"metadata_field": "is_equal_to_this"},
    where_document={"$contains":"search_string"}
)

collection.query(
    query_texts=["doc10", "thus spake zarathustra", ...],
    n_results=10,
    where={"metadata_field": "is_equal_to_this"},
    where_document={"$contains":"search_string"}
)

collection.get(
	ids=["id1", "id2", "id3", ...],
	where={"style": "style1"}
)



# Encode your query
query = "I am constructing a retrieval system."
query_embedding = model.encode([query])

# Query ChromaDB for the most similar sentence
results = collection.query(query_embeddings=query_embedding, n_results=1)

# Retrieve the most similar sentence
most_similar_sentence = results['metadatas'][0][0]["text"]
print("Most similar sentence:", most_similar_sentence)
