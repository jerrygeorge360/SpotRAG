# RAG-: Retrival-Augmented Generation

it has two main components
retriever-identifies and retrives relevant documents
generator-takes retrieved docs and the input query to generate coherent and contextually relevant response
RAG is a framework that combines the strengths of retrival-based systems and gneration-based models to produce more accurate and contextual relevant response


Naive RAG-deep dive
docs(parsing + prepossing) -->parsed docs(chunking)-->chunks-->embeding model(vectorize)-->vector store
user-->query-->embedding model-->vectorize-->vector store(retrieve)-->prompt relevant docs query-->gen llm(generate)-->response

challenges of naive RAG
1. limited contextual understanding
2. inconsistent relevance and quality of retrieved documents
3. Poor integration between retrieval and generation
4. Inefficient handling of Large Scale data
5. Lack of robustness and adaptability

summary
retrieval challenges:selection of misaligned or irrevant chunks
generative challenges:halluciantion,toxicity or bias outputs
vector databases (chromadb)

Advanced RAG techniques
introduces specific improvements to overcome the limitations of NAIVE RAG.Focuses on enhancing retrieval quality
1. Pre-retrieval (improvent of indexing structure and user query,imporove data details ,organizing indexes better,adding extra info,aligning correctly)


2. Post-retrieval(re ranking to highlight the most important content)

Query Expansion(with generated answers)
Generate potential answers to the query(using llm) to get relevant context

query->llm->answer->vector db->query results->llm-->llm
query-->vector db

use cases
1. Information retrieval
2. Question Answering Systems
3. E-commerce Search
4. Academic Research

Downsides
noise
'''
import os

from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

load_dotenv()
open_ai_key = os.getenv('OPEN_AI_KEY')

## IN USING SPOTIFY API
I  would use client credentials and authorization code flow
client credentials flow:is for accessing public data
authorization code flow: is for accessing private data 

## workflow update

```
User Prompt → Intent Classifier → Narrowed Collection(s) → User Prompt → Vector Search → Retrieve Top Docs → LLM Prompt → Generate Response (Naive RAG)
```
```
User Prompt → LLM → Hallucinated Response + User Prompt → Intent Classifier → Narrowed Collection(s) → Hallucinated Response + User Prompt → Vector Search → Retrieve Top Docs → LLM Prompt → Generate Response (Advanced RAG)
```









