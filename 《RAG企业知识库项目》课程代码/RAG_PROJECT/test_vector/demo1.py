
from llm_models.embeddings_model import bge_embedding

# sentence_transformers


embeddings = bge_embedding.embed_documents(
    [
        "Hi there!",
        "Oh, hello!",
        "What's your name?",
        "My friends call me World",
        "Hello World!"
    ]
)
print(len(embeddings), len(embeddings[0]))

embedded_query = bge_embedding.embed_query("What was the name mentioned in the conversation?")
print(embedded_query)