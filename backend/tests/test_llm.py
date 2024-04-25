import pytest
from chat_microservice.llm import get_oai_client, get_wv_client
import openai

# def test_get_and_close_oai(app):
#     with app.app_context():
#         oai_client = get_oai_client()
#         assert oai_client is get_oai_client()

#     with pytest.raises(openai.APIConnectionError):
#         _ = oai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": "Hello!"}
#             ]
#         )

# ToDo: write unit test for testing connection to the weviate client
