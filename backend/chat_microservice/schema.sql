DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS conversation;
DROP TABLE IF EXISTS message;

CREATE TABLE user(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE conversation(
    conv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tag_description TEXT NOT NULL,
    started_date TEXT NOT NULL,
    most_recent_entry_date TEXT NOT NULL
);

CREATE TABLE message(
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conv_id INTEGER NOT NULL,
    conv_offset INTEGER NOT NULL,
    sender_role TEXT CHECK(sender_role in ('user', 'bot')) NOT NULL,
    content TEXT NOT NULL
);