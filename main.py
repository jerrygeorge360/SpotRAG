# install chroma
import chromadb
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("paraphrase-albert-small-v2")
client = chromadb.Client()
# Sample sentences
sentences = ["I am building a RAG system.", "This is another sentence.", "Embedding systems are fun!"]

embedding = model.encode(sentences)
collection = client.create_collection("sentence_embeddings")
for i, sentence in enumerate(sentences):
    collection.add([str(i)], embedding[i], metadatas=[{"text": sentence}])



# Encode your query
query = "I am constructing a retrieval system."
query_embedding = model.encode([query])

# Query ChromaDB for the most similar sentence
results = collection.query(query_embeddings=query_embedding, n_results=1)

# Retrieve the most similar sentence
most_similar_sentence = results['metadatas'][0][0]["text"]
print("Most similar sentence:", most_similar_sentence)
