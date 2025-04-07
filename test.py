from chromaclass import  *
chroma = Chroma(client_config)

# Create and switch collections
chroma.create_collection("songs", {'bieber':'love yourself'})
chroma.create_collection("artists", {'bellion':'goat'})

chroma.use_collection("songs")


# Or directly add/query a specific one
chroma.query_collection({"query": ["lofi beats"]}, name="songs")

print(chroma.peek())