from flask import (
    Blueprint, g, jsonify, request
)


from chat_microservice.db import (
    drop_messages_after_inclusive,
    insert_new_conversation,
    insert_new_message,
    select_all_conversations,
    select_all_messages,
    select_conversation,
    select_previous_messages,
    select_user_by_id
)

from chat_microservice.llm import (
    get_assistant_completion,
    get_assistant_completion_rag
)

from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route("/test", methods=["GET"])
@jwt_required()
def test_route():
    user_id = get_jwt_identity()
    username = get_jwt()["username"]
    return jsonify({"msg": f"hello {user_id}, {username}"})


@chat_bp.route("/allConversations", methods=["GET"])
@jwt_required()
def all_conversations():
    user_id = get_jwt_identity()
    data = select_all_conversations(user_id)
    return jsonify(data), 200


@chat_bp.route("/conversation", methods=["GET", "POST"])
@jwt_required()
def conversation():
    user_id = get_jwt_identity()
    if request.method == "POST":
        # ToDo: add some error handling to handle bad database connections etc
        new_conv_id = insert_new_conversation(user_id)
        return jsonify({"conv_id": new_conv_id}), 200
    elif request.method == "GET":
        # return information about the conversation that the user wants to have
        # ToDo: this will break on the client side because fetch doenst like
        # taking JSON input for the request body
        # change to use arguments in the get request instead of JSON body
        data = request.get_json()
        if "conv_id" not in data:
            return jsonify({"msg": "request needs conv_id attribute"}), 400
        conv_id = data["conv_id"]
        # ToDo: handle none return from select conversation in case of 404 conversation not found
        ret_dict = select_conversation(conv_id)
        return jsonify(ret_dict), 200


@chat_bp.route("/allMessages", methods=["GET"])
@jwt_required()
def all_messages():
    # user_id = get_jwt_identity()
    conv_id = request.args.get("conv_id")
    if not conv_id:
        return jsonify({"msg": "request needs to include \"conv_id\""}), 400
    ret_list = select_all_messages(conv_id)
    return jsonify(ret_list), 200


# Design choice: write the user message to the database last with the bot response so that
# if the oai api call fails there isnt two copies of the user message in the db when the user
# repeats their message

# For new messages at the end of the conversation the conv_offset should be one greater than the last
# conv_offset in the message history
@chat_bp.route("/newMessage", methods=["POST"])
@jwt_required()
def new_message():
    user_id = get_jwt_identity()
    data = request.get_json()
    if "conv_id" not in data:
        return jsonify({"msg": "request must contain conv_id"}), 400
    if "conv_offset" not in data:
        return jsonify({"msg": "request must contain conv_offset"}), 400
    if "content" not in data:
        return jsonify({"msg": "request must contain content"}), 400
    conv_id = data["conv_id"]
    incoming_user_message_offset = data["conv_offset"]
    incoming_user_message_content = data["content"]

    # check that the userId and convId are a valid pair, the user associated with that conversation must be the same user
    conversation = select_conversation(conv_id=conv_id)
    user = select_user_by_id()
    if not user:
        return jsonify({"msg": f"user with user_id: {user_id} not found"}, 404)
    if not conversation:
        return jsonify({"msg": f"Conversation with conv_id {conv_id} not found"}, 404)
    if user["user_id"] != conversation["user_id"]:
        return jsonify({"msg": "you do not have permission to message this conversation"}, 403)

    # send user message to oai endpoint to get a text embedding
    # send text embedding to vector database to search for relevant context
    # read the conversation history up to this point (before the message conv_offset)
    conv_history = select_previous_messages(
        conv_id, incoming_user_message_offset)
    # ToDo: this is not the best syntax
    messages = [{"role": message["sender_role"],
                 "content": message["content"]} for message in conv_history]
    messages.append({"role":"user", "content":incoming_user_message_content})
    print("inside /newMessage, messages list: \n")
    for message in messages:
        print(message)
    # oai_chat_completion_stub = f"this is assistant response at offset {incoming_user_message_offset + 1}"
    # assistant_message = get_assistant_completion(messages=messages)
    assistant_message = get_assistant_completion_rag(messages)
    print("inside /newMessage")
    print(assistant_message)
    # append context to last message
    # send in order message conversation history with context to oai endpoint
    drop_messages_after_inclusive(conv_id, incoming_user_message_offset)
    # add the user message to the database
    insert_new_message(conv_id, incoming_user_message_offset,
                       "user", incoming_user_message_content)
    # add bot response to database
    insert_new_message(conv_id, incoming_user_message_offset +
                       1, 'assistant', assistant_message)
    # return bot response
    return jsonify({
        "conv_offset": incoming_user_message_offset + 1,
        "sender_role": 'assistant',
        "content": assistant_message
    }), 200
    # Backlog: allow the user to optionally view the appended context from vector db


# def get_client_OAI():
#     if g.client_OAI is not None:
#         return g.client_OAI
