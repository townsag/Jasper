from flask import current_app, g
import openai
from dotenv import dotenv_values
import weaviate
import weaviate.classes as wvc

def get_oai_client():
    if "oai_client" not in g:
        client_OAI = openai.OpenAI(api_key=current_app.config["OPENAI_API_KEY"])
        g.oai_client = client_OAI
    return g.oai_client

def get_wv_client():
    if "wv_client" not in g:
        client_WV = weaviate.connect_to_local()
        g.wv_client = client_WV
    return g.wv_client

def close_oai_client(e=None):
    if "oai_client" in g:
        g.oai_client.close()

def close_wv_client(e=None):
    if "wv_client" in g:
        g.wv_client.close()

def init_app(app):
    app.teardown_appcontext(close_oai_client)
    app.teardown_appcontext(close_wv_client)

def build_prompt_rag(context: list[str], query: str) -> str:
    prompt = "Context information is below\n----------\n"
    for chunk in context:
        prompt += chunk + "\n----------\n"
    prompt += "Given the context information and the user query, answer the query\n"
    prompt += "Query: " + query
    return prompt

def get_assistant_completion(messages: list[str]):
    oai_client = get_oai_client()
    completion_obj = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    ).choices[0].message
    return completion_obj.content

# get assistant completion rag modifies the contents of the messages list
def get_assistant_completion_rag(messages: list[str]):
    # config = dotenv_values(".env")
    # print("inside get assistint response rag, config: ", config.keys())
    # collection_name = config.get("COLLECTION_NAME")
    collection_name = current_app.config["COLLECTION_NAME"]
    print("inside get assistant completion, collection name:", collection_name)
    oai_client = get_oai_client()
    wv_client = get_wv_client()

    query = messages[-1]["content"]
    query_embed_response = oai_client.embeddings.create(input=query, model="text-embedding-3-small")
    query_embed_vector = query_embed_response.data[0].embedding

    wv_collection = wv_client.collections.get(collection_name)
    db_response = wv_collection.query.near_vector(
        near_vector=query_embed_vector,
        limit=2,
        return_metadata=wvc.query.MetadataQuery(certainty=True)
    )

    context = [object.properties["chunk_text"] for object in db_response.objects]
    prompt_rag = build_prompt_rag(context, query)
    print("inside get assistant completion rag")
    print(prompt_rag)
    messages[-1]["content"] = prompt_rag

    completion_obj = oai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    ).choices[0].message
    return completion_obj.content