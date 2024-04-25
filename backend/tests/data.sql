INSERT INTO user (username, password) VALUES 
("asdf", "scrypt:32768:8:1$Jo4B9BMZWHl56S3F$ec9dfc567e81317128438af72996eaa96ac85d5668288786d2d8fe6526e819b6c4986e059ea15149441b2c3198193c9f18438c3024f78d229c168378f6886d5c");

INSERT INTO conversation (conv_id, user_id, tag_description, started_date, most_recent_entry_date)
VALUES
(1, 1, 'How to sew', '2024-04-03T17:57:26.142730', '2024-04-03T17:57:26.142730'),
(2, 1, 'What are frogs', '2024-04-03T22:04:57.365630', '2024-04-03T22:04:57.365630');

INSERT INTO message (message_id, conv_id, conv_offset, sender_role, content) VALUES
(1, 1, 1, 'user', 'How should I start sewing'),
(2, 1, 2, 'assistant', 'First gather all the necessary materials, then find a pattern for a piece you want to make, then sew the piece'),
(3, 2, 1, 'user', 'Please tell me about frongs, specifically what they are'),
(4, 2, 2, 'assistant', 'Frogs are amphibious woodland creatures that eat flies.');