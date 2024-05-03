import pytest
import json
from chat_microservice.db import get_db
import sqlite3

from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

@pytest.mark.parametrize(
    ("route"),
    (("/chat/allConversations"), ("/chat/conversation"), ("/chat/allMessages"))
)
def test_auth_required_get(client, route):
    response = client.get(route)
    assert response.status_code == 401

@pytest.mark.parametrize(
    ("route"),
    (("/chat/conversation"), ("/chat/newMessage"))
)
def test_auth_required_post(client, route):
    response = client.post(route)
    assert response.status_code == 401

# ToDo: test the behavior of the endpoints when we deliberately close the database
# connection before/during the request

class TestAllConversationsEndpoint:
    # what are we testing with this function: 
    #   * We can get valid data when authenticated (be sure to test that the data is in the correct order)
    #   - test that 404 response when there was an authenticated user thats not in the database 
    #       - (how do I test this..? This may be unreachable)
    #       - hod do I authenticate a user that is not in the database, how would they get a valid JWT
    #   * test that we get an empty list when there is a user with no conversation history
    # Both client and auth are created from the same instance of the flask app so even 
    # though they are different objects they are using the same client under the hood
    @pytest.mark.parametrize(
            ("username", "password", "expected_data"),
            (
                ("asdf", "asdf", [
                    {
                        "conv_id": 2,
                        "most_recent_entry_date": "2024-04-03T22:04:57.365630",
                        "started_date": "2024-04-03T22:04:57.365630",
                        "tag_description":'What are frogs',
                        "user_id": 1
                    },
                    {
                        "conv_id": 1,
                        "most_recent_entry_date": "2024-04-03T17:57:26.142730",
                        "started_date": "2024-04-03T17:57:26.142730",
                        "tag_description": 'How to sew',
                        "user_id": 1
                    }
                ]),
            ("empty_user", "empty_user", [])
        )
    )
    def test_get_all_conversations(self, client, auth, username, password, expected_data):
        JWT_str, _ = auth.login_with_jwt(username, password)
        response = client.get(
            "/chat/allConversations",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            }
        )
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data == expected_data


class TestConversationEndpoint:
    # what are we testing with this function
    #   - post
    #       - check the database to see if the new conversation was created
    #       - use the returned new conversation ID to check that it is in the db
    def test_conversation_post(self, app, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_conversation = client.post(
            "/chat/conversation",
            headers={
                "Content-Type":"application/json",
                "Authorization":f"Bearer {JWT_str}"
            }
        )
        assert response_conversation.status_code == 200
        new_conv_id = json.loads(response_conversation.get_data(as_text=True)).get("conv_id")

        with app.app_context():
            db_connection = get_db()
            db_cursor = db_connection.cursor()
            ret_row = db_cursor.execute(
                "SELECT * FROM conversation WHERE conv_id=?",
                (new_conv_id,)
            ).fetchone()
            # return type of ret_conv_id should be a single dictionary
            assert ret_row["conv_id"] == new_conv_id
            db_cursor.close()

    # what are we testing with this function
    #   - get
    #       - test that the returned data for one of the conversations is correct
    def test_conversation_get(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_conversation = client.get(
            "/chat/conversation",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            },
            query_string={
                "conv_id":1
            }
        )
        assert response_conversation.status_code == 200
        expected_data = {
            "conv_id": 1,
            "user_id": 1,
            "tag_description": "How to sew",
            "started_date": "2024-04-03T17:57:26.142730",
            "most_recent_entry_date": "2024-04-03T17:57:26.142730"
        }
        assert json.loads(response_conversation.get_data(as_text=True)) == expected_data

    # what are we testing with this function
    #   - get
    #       - check that a get for a conv_id not in the db returns an error
    #       - check that attempting to view a conv_id belonging to a different user returns an error
    @pytest.mark.parametrize(
            ("conv_id", "status_code", "expected_value"),
            (
                (100, 404, "no conversation found with that conv_id"),
                (3, 403, "attempting to view a conversation that does not beling to this user")
            )
    )
    def test_conversation_get_error(self, client, auth, conv_id, status_code, expected_value):
        response_login = auth.login()
        JWT_str = json.loads(response_login.get_data(as_text=True)).get("access_token")
        headers = { "Authorization":f"Bearer {JWT_str}" }
        params = { "conv_id":conv_id }
        response_conversation = client.get("/chat/conversation", headers=headers, query_string=params)
        assert response_conversation.status_code == status_code
        response_data = json.loads(response_conversation.get_data(as_text=True))
        assert response_data.get("msg") == expected_value

    # what are we testing with this function
    #   - get
    #       - test that a get with no conv_id returns an error
    def test_conversation_get_missing(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_conversation = client.get(
            "/chat/conversation",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            }
        )
        assert response_conversation.status_code == 400
        assert json.loads(response_conversation.get_data(as_text=True)).get("msg") == "request needs conv_id attribute"



class TestAllMessages:
    # what are we testing with this function
    #   - get
    #       - all the expected content is returned in a list of dictionaries
    def test_messages_get(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_messages = client.get(
            "/chat/allMessages",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            },
            query_string={
                "conv_id":2
            }
        )
        expected_data = [
            {
                "conv_id": 2,
                "conv_offset": 1,
                "sender_role": "user",
                "content": "Please tell me about frongs, specifically what they are"
            },{
                "conv_id": 2,
                "conv_offset": 2,
                "sender_role": "assistant",
                "content": "Frogs are amphibious woodland creatures that eat flies."
            }
        ]
        assert response_messages.status_code == 200
        assert json.loads(response_messages.get_data(as_text=True)) == expected_data

    # what are we testing with this function
    #   - get
    #       - users can't request message histories for conversations that they dont belong to
    def test_messages_wrong_user(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_messages = client.get(
            "/chat/allMessages",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            },
            query_string={
                "conv_id":3
            }
        )
        assert response_messages.status_code == 403
        assert json.loads(response_messages.get_data(as_text=True)).get("msg") == "attempting to view conversation that does not belong to this user"

    # what are we testing with this function
    #   - get
    #       - requests without a conversation ID return an error
    def test_messages_no_id(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_messages = client.get(
            "/chat/allMessages",
            headers={
                "Authorization": f"Bearer {JWT_str}"
            }
        )
        assert response_messages.status_code == 400
        assert json.loads(response_messages.get_data(as_text=True)).get("msg") == "request needs to include conv_id param"

    # what are we testing with this function
    #   - get
    #       - requests for messages in a conversation that does not exist return an error
    def test_messages_not_exist(self, client, auth):
        JWT_str, _ = auth.login_with_jwt()
        response_messages = client.get(
            "/chat/allMessages",
            headers={
                "Authorization":f"Bearer {JWT_str}"
            },
            query_string={
                "conv_id": 500
            }
        )
        assert response_messages.status_code == 404
        assert json.loads(response_messages.get_data(as_text=True)).get("msg") == "no conversation found with that conv_id"


# def create_chat_completion(response: str, role: str = "assitant"):
#     return ChatCompletion(

#     )

"""
class TestNewMessageEndpoint:
    # what are we testing here
    #   - post
    #       - if the username in the JWT doesnt exist return an error (this may be unreachable code without editing the JWT)
    #       - if the open ai api call fails we should return an error and not store the users message in the database
    #           - use monkeypatch to simulate failure behavior of open ai client completion

    # what are we testing here
    #   - post
    #       - if a read from the database for the message history fails we should return an error
    #           - use monkeypatch to simulate sqlite failure behavior

    # what are we testing here
    #   - post
    #       - if the write to the database for the user message fails we should return an error
    #           - use monkeypatch to simulate sqlite failure behavior

    # what are we testing here
    #   - post
    #       - if the retrival from the weaviate database fails return an error
    #           - use monkeypatch to simulate weaviate failure behavior

    # what are we testing here
    #   - post
    #       - test that the new message is inserted into the database
    #       - test that the agent completion is inserted into the database
    #           - use monkeypatch to overwrite successful behavior of open ai api call

    # what are we testing here
    #   - post
    #       - check that requests with message offset in the past overwrite old data



    # ToDo: add monkeypatch for weaviate and openai api
    # what are we testing here
    #   - post
    #       - check that requests with non matching userid and conversation id return an error
    #       - check that requests for conversation ids that dont exist return an error
    #       - check that requests with "" empty content return an error
    #       - check that requests with invalid offset return an error (in the future, 0 or negative)
    @pytest.mark.parametrize(
            ("conv_id", "conv_offset", "content", "expected_status", "expected_message"),
            (
                (3, 1, "how many doors are there", 403, "you do not have permission to message this conversation"),
                (100, 1, "Which bear is best?", 404, "Conversation with conv_id 100 not found"),
                (1, 3, "", 400, "message ccontent cannot be empty"),
                (1, 100, "This conversation is happening in the future", 409, "this message offset is not consistent with conversation history"),
                (1, 0, "This message is from before time", 400, "cannot process messages with offset < 1")
            )
    )
    def test_new_message_invalid(self, client, auth, conv_id, conv_offset, content, expected_status, expected_message):
        JWT_str, _ = auth.login_with_jwt()
        response_new_message = client.post(
            "/chat/newMessage",
            headers={
                "Authorization":f"Bearer {JWT_str}",
                "Content-Type":"application/json"
            },
            data=json.dumps({
                "conv_id":conv_id,
                "conv_offset":conv_offset,
                "content":content
            })
        )

        response_data = json.loads(response_new_message.get_data(as_text=True))
        assert response_new_message.status_code == expected_status
        assert response_data.get("msg") == expected_message

    # what are we testing here
    #   - post
    #       - if the request is missing conv_id return an error 
    #       - if the request is missing conv_offset return an error
    #       - if the request is missing content return an error
"""