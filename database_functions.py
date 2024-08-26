from db import db
from sqlalchemy.sql import text


def forum_setup(username, hash_value, title, subtitle):
    try:
        sql = "INSERT INTO users (username, password, admin) VALUES (:username, :password, TRUE)"
        sql2 = "INSERT INTO headings (heading_name, order_index) VALUES (:title, 1)"
        db.session.execute(text(sql), {"username":username, "password":hash_value})
        db.session.execute(text(sql2), {"title":title})
        if subtitle:
            sql3 =  "INSERT INTO headings (heading_name, order_index) VALUES (:subtitle, 2)"
            db.session.execute(text(sql3), {"subtitle":subtitle})
        db.session.commit()
        return True
    except:
        return False


# USERS

def register_user(username, password):
    try:
        sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
        db.session.execute(text(sql), {"username":username, "password":password})
        db.session.commit()
        return True
    except:
        return False

def check_username(username):
    sql = "SELECT 1 FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    return result.fetchone()

def fetch_password(username):
    sql = "SELECT password FROM users WHERE username=:username"
    result = db.session.execute(text(sql), {"username":username})
    hash_value = result.fetchone()
    return hash_value[0]

def is_admin(username):
    sql = "SELECT 1 FROM users WHERE username=:username AND admin='True'"
    result = db.session.execute(text(sql), {"username":username})
    return result.fetchone()


# NEW

def new_title(title):
    sql = "INSERT INTO headings (heading_name, order_index) VALUES (:title, 1) ON CONFLICT (order_index) DO UPDATE SET heading_name = :title"
    db.session.execute(text(sql), {"title":title})
    db.session.commit()

def new_subtitle(subtitle):
    sql = "INSERT INTO headings (heading_name, order_index) VALUES (:subtitle, 2) ON CONFLICT (order_index) DO UPDATE SET heading_name = :subtitle"
    db.session.execute(text(sql), {"subtitle":subtitle})
    db.session.commit()

def new_heading(heading_name):
    order_index = len(fetch_headings()) + 3
    sql = "INSERT INTO headings (heading_name, order_index) VALUES (:heading_name, :order_index)"
    db.session.execute(text(sql), {"heading_name":heading_name, "order_index":order_index})
    db.session.commit()

def new_subforum(subforum, heading_id):
    sql = "SELECT COUNT(subforum_id) FROM subforums WHERE heading_id=:heading_id"
    result = db.session.execute(text(sql), {"heading_id":heading_id})
    order_index = result.fetchone()[0]+1
    sql = "INSERT INTO subforums (heading_id, subforum_name, order_index) VALUES (:heading_id, :subforum, :order_index)"
    db.session.execute(text(sql), {"heading_id":heading_id, "subforum":subforum, "order_index":order_index})
    db.session.commit()    

def new_topic(topic_id, message, subforum_id, sender):
    sql = "INSERT INTO topics (subforum_id, topic_name, created, updated) VALUES (:subforum_id, :topic, NOW(), NOW()) RETURNING topic_id"
    result = db.session.execute(text(sql), {"subforum_id":subforum_id, "topic":topic_id})
    topic_id = result.fetchone()
    sql = "INSERT INTO messages (topic_id, message, sender, time) VALUES (:topic_id, :message, :sender, NOW())"
    db.session.execute(text(sql), {"topic_id":topic_id[0], "message":message, "sender":sender})
    db.session.commit()
    return topic_id[0]

def new_message(topic_id, message, sender):
    sql = "INSERT INTO messages (topic_id, message, sender, time) VALUES (:topic_id, :message, :sender, NOW())"
    db.session.execute(text(sql), {"topic_id":topic_id, "message":message, "sender":sender})
    db.session.commit()


# GET

def fetch_title():
    sql = "SELECT heading_name, heading_id FROM headings WHERE order_index < 3 ORDER BY order_index"
    result = db.session.execute(text(sql))
    titles = result.fetchall()
    while len(titles) <2:
        titles.append("")
    return titles

def fetch_headings():
    sql = "SELECT heading_name, heading_id FROM headings WHERE order_index >= 3 ORDER BY order_index"
    result = db.session.execute(text(sql))
    headings = result.fetchall()
    return headings

def fetch_subforum_by_topic(topic_id):
    sql = "SELECT s.subforum_name, s.subforum_id FROM topics t LEFT JOIN subforums s ON t.subforum_id=s.subforum_id WHERE t.topic_id=:topic_id"
    result = db.session.execute(text(sql), {"topic_id":topic_id})
    topics = result.fetchone()
    return topics

def fetch_subforum_by_id(subforum_id):
    sql = "SELECT subforum_name, subforum_id FROM subforums WHERE subforum_id=:subforum_id"
    result = db.session.execute(text(sql), {"subforum_id":subforum_id})
    topics = result.fetchone()
    return topics
    
def subforum_list():
    sql = "SELECT subforum_name, subforum_id FROM subforums ORDER BY subforum_id, order_index"
    result = db.session.execute(text(sql))
    subforums = result.fetchall()
    return subforums

def fetch_topic(topic_id):
    sql = "SELECT topic_name, topic_id FROM topics WHERE topic_id=:topic_id ORDER BY pinned, updated"
    result = db.session.execute(text(sql), {"topic_id":topic_id})
    topic = result.fetchone()
    return topic

def headings_and_subforums2():
    sql = "SELECT h.order_index, s.order_index, h.heading_name h_name, s.subforum_name s_name, s.subforum_id s_id, COUNT(DISTINCT t.topic_id) topic_count, COUNT(m.message_id) message_count \
        FROM headings h LEFT JOIN subforums s ON h.heading_id=s.heading_id LEFT JOIN topics t ON s.subforum_id=t.subforum_id LEFT JOIN messages m ON t.topic_id=m.topic_id \
        WHERE h.order_index > 2 GROUP BY h_name, h.order_index, s_name, s.order_index, s_id ORDER BY h.order_index, s.order_index"
    result = db.session.execute(text(sql))
    query_result = result.fetchall()
    forum_structure = {}
    for item in query_result:
        if item.h_name not in forum_structure:
            forum_structure[item.h_name] = []
        if item.s_id:
            forum_structure[item.h_name].append(item[3:])
    return forum_structure

def index_page():
    sql = "SELECT a.h_ind, a.s_ind, a.h_name h_name, a.s_id s_id, a.s_name, a.topic_count, a.message_count, c.topic_name, b.sender, b.time \
        FROM (SELECT h.order_index h_ind, s.order_index s_ind, h.heading_name h_name, s.subforum_name s_name, s.subforum_id s_id, COUNT(DISTINCT t.topic_id) topic_count, COUNT(m.message_id) message_count, MAX(a.message_id) message_id \
        FROM headings h LEFT JOIN subforums s ON h.heading_id=s.heading_id LEFT JOIN topics t ON s.subforum_id=t.subforum_id LEFT JOIN messages m ON t.topic_id=m.topic_id LEFT JOIN messages a ON m.message_id=a.message_id \
        WHERE h.order_index > 2 GROUP BY h_name, h.order_index, s_name, s.order_index, s_id ORDER BY h.order_index, s.order_index) a \
        LEFT JOIN messages b ON a.message_id=b.message_id LEFT JOIN topics c ON b.topic_id=c.topic_id"
    result = db.session.execute(text(sql))
    query_result = result.fetchall()
    forum_structure = {}
    for item in query_result:
        if item.h_name not in forum_structure:
            forum_structure[item.h_name] = []
        if item.s_id:
            forum_structure[item.h_name].append(item[3:])
    return forum_structure

def subforum_page(id):
    sql = "SELECT a.t_name t_name, a.t_id t_id, a.pinned pinned, a.m_count-1 m_count, b.time min_time, b.sender min_sender, c.time max_time, c.sender max_sender \
        FROM (SELECT t.topic_name t_name, t.topic_id t_id, t.pinned pinned, COUNT(m.message_id) m_count, MIN(m.message_id) min_message, MAX(m.message_id) max_message\
        FROM topics t LEFT JOIN messages m ON t.topic_id=m.topic_id WHERE subforum_id=:id \
        GROUP BY t_name, t_id ORDER BY pinned, max_message DESC) a \
        LEFT JOIN messages b ON a.min_message=b.message_id LEFT JOIN messages c ON a.max_message=c.message_id ORDER BY max_time DESC"
    result = db.session.execute(text(sql), {"id":id})
    topics = result.fetchall()
    return topics

def topic_page(topic_id):
    sql = "SELECT message, sender, time FROM messages WHERE topic_id=:topic_id ORDER BY time"
    result = db.session.execute(text(sql), {"topic_id":topic_id})
    messages = result.fetchall()
    return messages


# UPDATE

def update_order_index(order_index: list, ids: list, category: str):
    order = sorted(zip(order_index, ids))
    if category == "heading":
        sql = "UPDATE headings SET order_index = :i WHERE heading_id =:id"
        order = [(index+3, x[1]) for index, x in enumerate(order)]
    if category == "subforum":
        sql = "UPDATE subforums SET order_index = :i WHERE subforum_id =:id"
        order = [(index+1, x[1]) for index, x in enumerate(order)]
    # temporary index
    for item in order:
        db.session.execute(text(sql), {"i":item[0]+100000, "id":item[1]})
    # permanent index
    for item in order:
        db.session.execute(text(sql), {"i":item[0], "id":item[1]})
    db.session.commit() 

def update_heading(heading_name, heading_id):
    sql = "UPDATE headings SET heading_name = :heading_name WHERE heading_id = :heading_id"
    db.session.execute(text(sql), {"heading_name":heading_name, "heading_id":heading_id})
    db.session.commit()

def update_subforum_name(subforum_name, subforum_id):
    sql = "UPDATE subforums SET subforum_name =:subforum_name WHERE subforum_id =:subforum_id"
    db.session.execute(text(sql), {"name":subforum_name, "subforum_id":subforum_id})
    db.session.commit()


# SEARCH 

def search_from_topic(word, topic_id):
    sql = "SELECT m.sender sender, m.message message, m.time time, t.topic_name topic \
        FROM messages m LEFT JOIN topics t ON m.topic_id=t.topic_id WHERE m.topic_id=:topic_id AND m.message ~* :query"
    result = db.session.execute(text(sql), {"topic_id":topic_id, "query":word})
    messages = result.fetchall()
    return messages

def search(word, sender, subforums, time):
    sql1 = " AND s.subforum_id = ANY(:subforums)" if subforums else ""
    sql2 = " AND m.time >= NOW() - interval :time DAY" if time else ""
    sql =  "SELECT m.sender sender, m.time time, m.message message, t.topic_name topic \
        FROM messages m LEFT JOIN topics t ON m.topic_id=t.topic_id LEFT JOIN subforums s ON t.subforum_id=s.subforum_id \
        WHERE (m.message ~* :word OR t.topic_name ~* :word)\
        AND m.sender ~* :sender" + sql1 + sql2 + " ORDER BY m.message_id DESC"
    result = db.session.execute(text(sql), {"word":word, "sender":sender, "subforums":subforums, "time":time})
    messages = result.fetchall()
    return messages

