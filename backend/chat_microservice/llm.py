from flask import current_app, g
import openai
import weaviate
import weaviate.classes as wvc

# This doesnt do anything because the g variable is only global to the application
# context and a new application context is made for every request
# def init_oai_client():
#     print("inside inite oai client\n** making a new client")
#     client_OAI = openai.OpenAI(api_key=current_app.config["OPENAI_API_KEY"])
#     g.oai_client = client_OAI
#     print("id of oai client inside init oai client: ", id(g.oai_client))

def get_oai_client():
    if "oai_client" not in g:
        client_OAI = openai.OpenAI(api_key=current_app.config["OPENAI_API_KEY"])
        g.oai_client = client_OAI
    return g.oai_client

def get_wv_client():
    if "wv_client" not in g:
        client_WV = weaviate.connect_to_local(
            host=current_app.config["VECTOR_DB_HOSTNAME"]
        )
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

# pull out the functionality using the open_ai connection and the weaviate connection to make
# monkeypatching easier when testing
# this is for two reasons:
#   - mocking the entire openai client object would be a lot of boilerplate
#   - when the chat_microservice module is imported all the imports that the chat microservice 
#       module makes are also resolved. This happens BEFORE the monkeypatches are applied.
#       pulling the functions that are to be patched out of functions that are imported inside
#       chat_microservice.chat ensures that those functions arent imported before the monkeypatches
#       are applied
#       - this is a bit hacky and I dont like it but it is the best way that I understand to test
#           the code so far
def make_embedding_vector(query: str, model="text-embedding-3-small"):
    oai_client = get_oai_client()
    query_embed_response = oai_client.embeddings.create(input=query, model=model)
    query_embed_vector = query_embed_response.data[0].embedding
    return query_embed_vector

def retrieve_relevant_context(query_embed_vector: list[float], collection_name: str,  k: int = 2):
    wv_client = get_wv_client()
    wv_collection = wv_client.collections.get(collection_name)
    db_response = wv_collection.query.near_vector(
        near_vector=query_embed_vector,
        limit=k,
        return_metadata=wvc.query.MetadataQuery(certainty=True)
    )
    context = [object.properties["chunk_text"] for object in db_response.objects]
    return context

def get_chat_completion(messages: list[dict[str,str]], model="gpt-3.5-turbo"):
    oai_client = get_oai_client()
    completion_message_obj = oai_client.chat.completions.create(
        model=model,
        messages=messages
    ).choices[0].message
    return completion_message_obj.content

# ToDo: add some error handling for getting rate limited by llm api etc
# get assistant completion rag modifies the contents of the messages list
# ToDo: add proper logging here, consider using Arise
def get_assistant_completion_rag(messages: list[str]):
    collection_name = current_app.config["COLLECTION_NAME"]

    # messages is gauranteed to be in order by message offset ascending
    query = messages[-1]["content"]

    query_embed_vector = make_embedding_vector(query)
    context = retrieve_relevant_context(query_embed_vector, collection_name)

    prompt_rag = build_prompt_rag(context, query)
    # print("inside get assistant completion rag")
    # print(prompt_rag)
    # replace the user query with the user query augemented by the retrieved context
    messages[-1]["content"] = prompt_rag

    agent_response = get_chat_completion(messages)
    return agent_response

#   - just like above, pulling the functionality that has to be mocked out of the functions that 
#       are imported by chat_microservice.chat is the best solution I have so far to the problem
#       of monkeypatching the functions after they already have been imported
def build_prompt_and_query(user_message: str, agent_message:str):
    prompt = "This is a user message:\n" + user_message + "\n----------\n"
    prompt += "this is an assistant message:\n" + agent_message
    prompt += "\n----------\nPlease create a short title for that conversation using 4 words or fewer"
    response_content = get_chat_completion([{"role":"user", "content":prompt}])
    if len(response_content) > 30:
        return response_content[:27] + "..."
    else:
        return response_content

def get_conversation_title(user_message: str, agent_message: str):
    return build_prompt_and_query(user_message, agent_message)
