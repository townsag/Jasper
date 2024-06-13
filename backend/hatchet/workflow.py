from .hatchet import hatchet
from hatchet_sdk import Context
import openai
import os
import weaviate
from weaviate.classes import wvc

# assumption to be verified:
#   -   this module imports the hatchet.py file which means that before this code is run
#       the code in hatchet.py is run 
#   -   that means that the environment variables will already be loaded by the hatchet.py file

@hatchet.workflow(name="vanilla-rag", on_events=["message:create"])
class VanillaRagWorkflow:
    def __init__(self):
        self.client_OAI = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.client_WV = weaviate.connect_to_local(
            host=os.environ.get("VECTOR_DB_HOSTNAME")
        )
        self.model = "text-embedding-3-small"
        self.collection_name = os.environ.get("COLLECTION_NAME")
        self.k = 2

    @hatchet.step()
    def start(self, context: Context):
        return {
            "status":"embedding query"
        }
    
    @hatchet.step(parents=["start"])
    def create_embedding(self, context: Context):
        messages = context.workflow_input()["messages"]
        query = messages[-1]["content"]
        query_embed_response = self.client_OAI.embeddings.create(input=query, model=self.model)
        query_embed_vector = query_embed_response.data[0].embedding
        return {
            "status":"retrieving relevant context",
            "embedding-vector":query_embed_vector
        }

    @hatchet.step(parents=["create_embedding"])
    def retrieve_relevant_context(self, context: Context):
        query_embed_vector = context.step_output("create_embedding")["embedding-vector"]
        wv_collection = self.client_WV.collections.get(self.collection_name)
        db_response = wv_collection.query.near_vector(
            near_vector=query_embed_vector,
            limit=self.k,
            return_metadata=wvc.query.MetadataQuery(certainty=True)
        )
        context = [object.properties["chunk_text"] for object in db_response.objects]
        return {
            "status":"generating response",
            "context":context
        }
    
    @hatchet.step(parents=["retrieve_relevant_context"])
    def 