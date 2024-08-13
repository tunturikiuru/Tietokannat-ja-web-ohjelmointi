CREATE TABLE headings (
    heading_id SERIAL PRIMARY KEY, 
    heading_name TEXT,
    order_index INTEGER UNIQUE);

CREATE TABLE subforums (
    subforum_id SERIAL PRIMARY KEY, 
    subforum_name TEXT NOT NULL,
    heading_id INTEGER REFERENCES headings(heading_id), 
    order_index INTEGER,
    private BOOLEAN DEFAULT FALSE,
    UNIQUE (heading_id, order_index));

CREATE TABLE topics (
    topic_id SERIAL PRIMARY KEY, 
    subforum_id INTEGER REFERENCES subforums(subforum_id), 
    topic_name TEXT NOT NULL,
    created TIMESTAMP, 
    updated TIMESTAMP,
    pinned BOOLEAN DEFAULT FALSE);

CREATE TABLE users(
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    admin BOOLEAN DEFAULT FALSE);

CREATE TABLE messages (
	message_id SERIAL PRIMARY KEY,
	topic_id INTEGER REFERENCES topics(topic_id),
	message TEXT,
	sender TEXT REFERENCES users(username),
	time TIMESTAMP);
