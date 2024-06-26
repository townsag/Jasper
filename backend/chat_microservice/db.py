import sqlite3

import click
from flask import current_app, g
from datetime import datetime

# g is short for global, it refers to information that should be global within
# the context of this request/ the application context

# g is a special object that is unique for each request. It is used to store
# data that might be accessed by multiple functions during the request.

# current_app is another special object that points to the Flask application
# handling the request


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            database=current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    if "db" in g:
        g.db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode("utf8"))


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    # app.teardown_appcontext() tells Flask to call that function when cleaning up
    # after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask
    # command. Like     $ flask --app flaskr init-db
    app.cli.add_command(init_db_command)


def insert_new_conversation(user_id: int):
    # create a new conversation named new conversation in the database
    now_str = datetime.now().isoformat()
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "INSERT INTO conversation (user_id, tag_description, started_date, most_recent_entry_date) VALUES (?, ?, ?, ?)",
        (user_id, "New Conversation", now_str, now_str)
    )
    conv_id = db_cursor.lastrowid
    db_connection.commit()
    db_cursor.close()
    return conv_id

def update_conversation_description(conv_id: int, new_description: str):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "UPDATE conversation SET tag_description=? WHERE conv_id=?",
        (new_description, conv_id)
    )
    db_connection.commit()
    db_cursor.close()
    return

def check_name_unique(username: str):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    name = db_cursor.execute(
        "SELECT username FROM user WHERE username=?",
        (username,)
    ).fetchone()

    if name:
        db_cursor.close()
        return False
    else:
        db_cursor.close()
        return True


def insert_new_user(username: str, password_hash: str):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "INSERT INTO user (username, password) VALUES (?,? )",
        (username, password_hash)
    )
    user_id = db_cursor.lastrowid
    db_connection.commit()
    db_cursor.close()
    return user_id


def select_user_by_username(username: str):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    user = db_cursor.execute(
        "SELECT * FROM user WHERE username=?",
        (username,)
    ).fetchone()
    if not user:
        db_cursor.close()
        return False
    else:
        data = {
            "user_id": user["user_id"],
            "username": user["username"],
            "password": user["password"]
        }
        db_cursor.close()
        return data
    
def select_user_by_id(user_id: int):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    user = db_cursor.execute(
        "SELECT * FROM user WHERE user_id=?",
        (user_id,)
    ).fetchone()
    if not user:
        db_cursor.close()
        return False
    data = {
        "user_id": user["user_id"],
        "username": user["username"],
        "password": user["password"]
    }
    db_cursor.close()
    return data


def select_conversation(conv_id: int):
    # ToDo: implement logic to handle errors like empty set in the select
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    conversation = db_cursor.execute(
        "SELECT * FROM conversation WHERE conv_id=?",
        (conv_id,)
    ).fetchone()

    if not conversation:
        db_cursor.close()
        return False

    data = {
        "conv_id": conversation[0],
        "user_id": conversation[1],
        "tag_description": conversation[2],
        "started_date": conversation[3],
        "most_recent_entry_date": conversation[4]
    }
    db_cursor.close()
    return data


def select_all_conversations(user_id: int):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    # ToDo: i am suspicious that this is not actually selecting the conversations in the correct order
    user_conversations = db_cursor.execute(
        "SELECT * FROM conversation WHERE user_id=? ORDER BY most_recent_entry_date DESC",
        (user_id,)
    ).fetchall()
    data = list()

    if not user_conversations:
        db_cursor.close()
        return False
    
    for conversation in user_conversations:
        data.append({
            "conv_id": conversation[0],
            "user_id": conversation[1],
            "tag_description": conversation[2],
            "started_date": conversation[3],
            "most_recent_entry_date": conversation[4]
        })
    db_cursor.close()
    return data


def select_all_messages(conv_id: int):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    user_conversation_messages = db_cursor.execute(
        "SELECT * FROM message WHERE conv_id=? ORDER BY conv_offset ASC",
        (conv_id,)
    ).fetchall()
    data = list()
    for message in user_conversation_messages:
        data.append({
            "conv_id": message[1],
            "conv_offset": message[2],
            "sender_role": message[3],
            "content":message[4]
        })
    db_cursor.close()
    return data


def select_previous_messages(conv_id: int, conv_offset: int):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    previous_messages = db_cursor.execute(
        "SELECT * FROM message WHERE conv_id=? AND conv_offset<? ORDER BY conv_offset ASC",
        (conv_id, conv_offset)
    ).fetchall()
    data = list()
    for row in previous_messages:
        data.append({
            "message_id": row[0],
            "conv_id": row[1],
            "conv_offset": row[2],
            "sender_role": row[3],
            "content": row[4]
        })
    db_cursor.close()
    return data


def drop_messages_after_inclusive(conv_id: int, conv_offset: int):
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    # drop all messages with offset gereater than or equal to the current message conv offset
    db_cursor.execute(
        "DELETE FROM message WHERE conv_id=? AND conv_offset>=?",
        (conv_id, conv_offset)
    )
    db_connection.commit()
    db_cursor.close()


def insert_new_message(conv_id: int, conv_offset: int, sender_role: str, content: str):
    # print(f"inserting message with offset {conv_offset}")
    db_connection = get_db()
    db_cursor = db_connection.cursor()
    db_cursor.execute(
        "INSERT INTO message (conv_id, conv_offset, sender_role, content) VALUES (?,?,?,?)",
        (conv_id, conv_offset, sender_role, content)
    )
    db_connection.commit()
    db_cursor.close()
