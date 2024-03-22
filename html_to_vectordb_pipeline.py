import weaviate
import weaviate.classes as wvc
import json
import openai
from dotenv import dotenv_values
from chunking_utils import chunk
import tiktoken
from bs4 import BeautifulSoup

CHUNK_MAX_TOKENS = 512
TOKENIZER = "cl100k_base"

def main():
    client_WV = weaviate.connect_to_local()

    config = dotenv_values(".env")
    client_OAI = openai.OpenAI(api_key=config.get("OPENAI_API_KEY"))
    encoding = tiktoken.get_encoding(TOKENIZER)
    
    input_file = open("crawl_jax_docs/jax_docs.json")
    data = json.load(input_file)
    
    output_file = open("parsed_chunked_embedded_jax.jsonl", "w")
    
    try:
        # jax_rag_collection = client_WV.collections.get("Jax_RAG")
        jax_rag_collection = client_WV.collections.create(
            "Jax_RAG",
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
            vector_index_config=wvc.config.Configure.VectorIndex.hnsw(
                # select prefered distance metric
                distance_metric=wvc.config.VectorDistances.COSINE
            ),
        )
        total_tokens = 0

        for page_data in data[:10]:
            page_url = page_data["source"]
            page_content = page_data["chunks"]
            page_chunks = chunk(BeautifulSoup(page_content, features="lxml"), CHUNK_MAX_TOKENS, encoding)
            data_to_store = list()

            if "_src" in page_url:
                continue

            per_page_tokens = 0
            for i, chunk_text in enumerate(page_chunks):
                response = client_OAI.embeddings.create(input=chunk_text, model="text-embedding-3-small")
                per_page_tokens += response.usage.total_tokens
                temp_embedding = response.data[0].embedding

                output_file.write(json.dumps(
                    {
                        "page_url":page_url,
                        "page_offset":i,
                        "chunk_text":chunk_text,
                        "vector_embedding":temp_embedding
                    }
                ) + "\n")

                data_to_store.append(
                    wvc.data.DataObject(
                        properties={
                            "page_offset":i,
                            "chunk_text":chunk_text,
                            "page_url":page_url
                        },
                        vector=temp_embedding
                    )
                )
            
            total_tokens += per_page_tokens
            print(f"count_tokens: {per_page_tokens} for page {page_url}")
            insert_result = jax_rag_collection.data.insert_many(data_to_store)
            print(f"errors: {insert_result.errors}")

        print("total tokens: ", total_tokens)

    finally:
        client_WV.close()
        client_OAI.close()
        input_file.close()
        output_file.close()


if __name__ == "__main__":
    main()
