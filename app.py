from flask import Flask
from flask import redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    titles = fetch_title()
    subforum_order = subforum_dict()
    return render_template("index.html", titles=titles, subforum_order=subforum_order) 

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    subforum = fetch_subforum_by_id(subforum_id)
    topics = fetch_topics(subforum_id)
    return render_template("subforum.html", subforum=subforum, topics=topics)

@app.route("/subforum/<int:id>/new_topic")
def create_new_topic(id):
    return render_template("new_topic.html", id=id)

@app.route("/subforum/<int:id>/new_topic/send", methods=["POST"])
def send_new_topic(id):
    title = request.form["title"]
    message = request.form["content"]
    id = new_topic(title, message, id)
    return redirect(url_for("topic", topic_id=id))

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    subforum = fetch_subforum_by_topic(topic_id)
    topic = fetch_topic(topic_id)
    messages = fetch_messages(topic_id)
    return render_template("topic.html", messages=messages, subforum=subforum, topic=topic)

@app.route("/topic/<int:topic_id>/new_message/")
def new_message(topic_id):
    topic = fetch_topic(topic_id)
    return render_template("new_message.html", topic=topic)

@app.route("/new_message/send", methods=["POST"])
def send_new_message():
    message = request.form["message"]
    topic_id = request.form["topic_id"]
    new_message(topic_id, message)
    return redirect(url_for("topic", topic_id=topic_id))


# SETTINGS
@app.route("/settings")
def settings():
    titles = fetch_title()
    return render_template("settings.html", titles=titles)

@app.route("/settings/headings")
def heading_settings():
    headings = fetch_headings()
    return render_template("heading_settings.html", headings=headings)

@app.route("/settings/subforums")
def subforums():
    headings = fetch_headings()
    subforums_list = subforum_list()
    subforums_dict = subforum_dict()
    return render_template("subforum_settings.html", headings=headings, subforums_list=subforums_list, subforums_dict=subforums_dict)

## Settings send
@app.route("/settings/send", methods=["POST"])
def send_settings():
    title = request.form["title"]
    if title != "":
        new_title(title)
    subtitle = request.form["subtitle"]
    if subtitle != "":
        new_subtitle(subtitle)
    else:
        pass
        # POISTA ALAOTSIKKO
    return redirect("/")

@app.route("/settings/heading_name/send", methods=["POST"])
def send_new_heading():
    heading_name = request.form["heading"]
    if heading_name != "":
        new_heading(heading_name)
    return redirect("/settings/headings")

@app.route("/settings/heading_rename/send", methods=["POST"])
def send_change_heading_name():
    heading_id = request.form["heading_id"]
    new_name = request.form["new_heading"]
    if new_name != "":
        sql = "UPDATE headings SET heading_name = :new_name WHERE heading_id = :heading_id"
        db.session.execute(text(sql), {"new_name":new_name, "heading_id":heading_id})
        db.session.commit()
    return redirect("/settings/headings")

@app.route("/settings/heading_order/send", methods=["POST"])
def send_heading_order():
    heading_order = request.form.getlist("heading_order")
    heading_ids = request.form.getlist("heading_id")
    update_order_index(heading_order, heading_ids, "heading")
    return redirect("/settings/headings")

@app.route("/settings/delete_heading/send", methods=["POST"])
def send_delete_heading():
    pass

@app.route("/new_subforum/send", methods=["POST"])
def send_subforum():
    subforum = request.form["new_subforum"]
    heading = request.form["heading"]
    new_subforum(subforum, heading)
    return redirect("/settings/subforums")

@app.route("/settings/subforum_rename/send", methods=["POST"])
def rename_subforum():
    subforum_id = request.form["old_name"]
    name = request.form["new_name"]
    if name != "":
        update_subforum_name(name, subforum_id)
    return redirect("/settings/subforums")

@app.route("/settings/subforum_order/send", methods=["POST"])
def update_subforum_order():
    subforum_order = request.form.getlist("subforum_order")
    subforum_ids = request.form.getlist("subforum_id")
    update_order_index(subforum_order, subforum_ids, "subforum")
    return redirect("/settings/subforums")


# DATABASE FUNCTIONS
## NEW
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

def new_topic(topic_id, message, subforum_id):
    sql = "INSERT INTO topics (subforum_id, topic_name, created, updated) VALUES (:subforum_id, :topic, NOW(), NOW()) RETURNING topic_id"
    result = db.session.execute(text(sql), {"subforum_id":subforum_id, "topic":topic_id})
    topic_id = result.fetchone()
    sql = "INSERT INTO messages (topic_id, message, time) VALUES (:topic_id, :message, NOW())"
    db.session.execute(text(sql), {"topic_id":topic_id[0], "message":message})
    db.session.commit()
    return topic_id[0]

def new_message(topic_id, message):
    sql = "INSERT INTO messages (topic_id, message, time) VALUES (:topic_id, :message, NOW())"
    db.session.execute(text(sql), {"topic_id":topic_id, "message":message})
    db.session.commit()

## GET
def fetch_title():
    sql = "SELECT heading_name, heading_id FROM headings WHERE order_index < 3 ORDER BY order_index"
    result = db.session.execute(text(sql))
    titles = result.fetchall()
    while len(titles) <2:
        titles.append(("", ""))
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

def subforum_dict():
    sql = "SELECT h.heading_name h_name, h.heading_id h_id, s.subforum_name s_name, s.subforum_id s_id FROM subforums s LEFT JOIN headings h ON h.heading_id = s. heading_id ORDER BY h.order_index, s.order_index"
    result = db.session.execute(text(sql))
    subforums = result.fetchall()
    subforum_order = {}
    for subforum in subforums:
        if (subforum.h_name, subforum.h_id) not in subforum_order:
            subforum_order[(subforum.h_name, subforum.h_id)] = []
        subforum_order[(subforum.h_name, subforum.h_id)].append((subforum.s_name, subforum.s_id))
    return subforum_order

def fetch_topic(topic_id):
    sql = "SELECT topic_name, topic_id FROM topics WHERE topic_id=:topic_id ORDER BY pinned, updated"
    result = db.session.execute(text(sql), {"topic_id":topic_id})
    topic = result.fetchone()
    return topic

# TODO VOIKO TRY-EXCEPT poistaa?
def fetch_topics(id):
    try:
        sql = "SELECT topic_name, topic_id FROM topics WHERE subforum_id=:id ORDER BY pinned, updated"
        result = db.session.execute(text(sql), {"id":id})
        topics = result.fetchall()
    except:
        topics = []
    return topics

def fetch_messages(topic_id):
    sql = "SELECT message, time FROM messages WHERE topic_id=:topic_id ORDER BY time"
    result = db.session.execute(text(sql), {"topic_id":topic_id})
    messages = result.fetchall()
    return messages

## UPDATE
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

def update_subforum_name(subforum_name, subforum_id):
    sql = "UPDATE subforums SET subforum_name =:subforum_name WHERE subforum_id =:subforum_id"
    db.session.execute(text(sql), {"name":subforum_name, "subforum_id":subforum_id})
    db.session.commit()

def update_heading_name(heading_name, heading_id):
    sql = "UPDATE headings SET heading_name = :heading_name WHERE heading_id = :heading_id"
    db.session.execute(text(sql), {"new_name":heading_name, "heading_id":heading_id})
    db.session.commit()



