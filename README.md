kurssin "Tietokannat ja web-ohjelmointi" materiaalin perusteella itsenäisesti tehty harjoitustyö

Tietokanta

CREATE TABLE headings (
    heading_id SERIAL PRIMARY KEY, 
    heading_name TEXT,
    order_index INTEGER UNIQUE);

CREATE TABLE subforums (
    subforum_id SERIAL PRIMARY KEY, 
    subforum_name TEXT NOT NULL,
    heading_id INTEGER REFERENCES headings(heading_id), 
    order_index INTEGER UNIQUE
    private BOOLEAN DEFAULT FALSE);

