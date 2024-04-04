import weaviate
import weaviate.classes as wvc
import json
import openai
from dotenv import dotenv_values
from chunking_utils import chunk
import tiktoken
from bs4 import BeautifulSoup
import time

CHUNK_MAX_TOKENS = 512
TOKENIZER = "cl100k_base"

def main():
    start = time.time()
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

        for page_number, page_data in enumerate(data):
            page_url = page_data["source"]
            if "_src" in page_url:
                print("=====skipping: ", page_url)
                continue

            print(f"\tDEBUG parsing {page_url}")
            page_content = page_data["chunks"]
            page_chunks = chunk(BeautifulSoup(page_content, features="lxml"), CHUNK_MAX_TOKENS, encoding)
            print(f"\tDEBUG: num chunks {len(page_chunks)}")
            
            # To embed multiple inputs in a single request, pass an array of strings or array of token arrays
            MAX_BATCH_SIZE = 2048
            batched_page_chunks = [page_chunks[batch_start:batch_start + MAX_BATCH_SIZE] for batch_start in range(0, len(page_chunks), MAX_BATCH_SIZE)]

            response_embedding_vectors = list()
            per_page_tokens = 0
            for batch_of_chunks in batched_page_chunks:
                response = client_OAI.embeddings.create(input=batch_of_chunks, model="text-embedding-3-small")
                response_embedding_vectors.extend([elem.embedding for elem in response.data])
                per_page_tokens += response.usage.total_tokens
            print(f"\tDEBUG: num embeddings {len(response_embedding_vectors)}")

            data_to_store = list()
            page_chunks_with_offset = [(offset, page_chunk) for offset, page_chunk in enumerate(page_chunks)]
            for (offset, page_chunk), embedding in zip(page_chunks_with_offset, response_embedding_vectors):
                output_file.write(json.dumps(
                    {
                        "page_url":page_url,
                        "page_offset":offset,
                        "chunk_text":page_chunk,
                        "vector_embedding":embedding
                    }
                ) + "\n")

                data_to_store.append(
                    wvc.data.DataObject(
                        properties={
                            "page_offset":offset,
                            "chunk_text":page_chunk,
                            "page_url":page_url
                        },
                        vector=embedding
                    )
                )
            print(f"\tDEBUG: num data objects {len(data_to_store)}")

            total_tokens += per_page_tokens
            print(f"count_tokens: {per_page_tokens} for page {page_url}")
            insert_result = jax_rag_collection.data.insert_many(data_to_store)
            print(f"errors: {insert_result.errors}")
            if page_number % 10 == 0:
                print(f"\n\npages so far: {page_number} total tokens so far: {total_tokens}\n")

    finally:
        client_WV.close()
        client_OAI.close()
        input_file.close()
        output_file.close()
        end = time.time()
        print("total tokens: ", total_tokens)
        print(f"total elapsed seconds: {end - start}")


if __name__ == "__main__":
    main()
