from flask import Flask
from flask import redirect, render_template, request, url_for, session
#from werkzeug.security import generate_password_hash
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import database_functions as dbf
import users


@app.route("/")
def index():
    titles = dbf.fetch_title()
    subforum_order = dbf.subforum_dict()
    return render_template("index.html", titles=titles, subforum_order=subforum_order) 

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    subforum = dbf.fetch_subforum_by_id(subforum_id)
    topics = dbf.fetch_topics(subforum_id)
    return render_template("subforum.html", subforum=subforum, topics=topics)

@app.route("/subforum/<int:id>/new_topic")
def create_new_topic(id):
    return render_template("new_topic.html", id=id)

@app.route("/subforum/<int:id>/new_topic/send", methods=["POST"])
def send_new_topic(id):
    title = request.form["title"]
    message = request.form["content"]
    id = dbf.new_topic(title, message, id)
    return redirect(url_for("topic", topic_id=id))

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    subforum = dbf.fetch_subforum_by_topic(topic_id)
    topic = dbf.fetch_topic(topic_id)
    messages = dbf.fetch_messages(topic_id)
    return render_template("topic.html", messages=messages, subforum=subforum, topic=topic)

@app.route("/topic/<int:topic_id>/new_message/")
def create_new_message(topic_id):
    topic = dbf.fetch_topic(topic_id)
    return render_template("new_message.html", topic=topic)

@app.route("/new_message/send", methods=["POST"])
def send_new_message():
    message = request.form["message"]
    topic_id = request.form["topic_id"]
    dbf.new_message(topic_id, message)
    return redirect(url_for("topic", topic_id=topic_id))


#USERS
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error_message = users.register_user(username, password1, password2)
        if error_message:
            return render_template("register.html", message=error_message)
        else:
            return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]        
        if users.login(username, password):
            return redirect("/")
    return render_template("login.html", message="Väärä käyttäjätunnus tai salasana")
    

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")



# SETTINGS
@app.route("/settings")
def settings():
    titles = dbf.fetch_title()
    return render_template("settings.html", titles=titles)

@app.route("/settings/headings")
def heading_settings():
    headings = dbf.fetch_headings()
    return render_template("heading_settings.html", headings=headings)

@app.route("/settings/subforums")
def subforums():
    headings = dbf.fetch_headings()
    subforums_list = dbf.subforum_list()
    subforums_dict = dbf.subforum_dict()
    return render_template("subforum_settings.html", headings=headings, subforums_list=subforums_list, subforums_dict=subforums_dict)

## Settings send
@app.route("/settings/send", methods=["POST"])
def send_settings():
    title = request.form["title"]
    if title != "":
        dbf.new_title(title)
    subtitle = request.form["subtitle"]
    if subtitle != "":
        dbf.new_subtitle(subtitle)
    else:
        pass
        # POISTA ALAOTSIKKO
    return redirect("/")

@app.route("/settings/heading_name/send", methods=["POST"])
def send_new_heading():
    heading_name = request.form["heading"]
    if heading_name != "":
        dbf.new_heading(heading_name)
    return redirect("/settings/headings")

@app.route("/settings/heading_rename/send", methods=["POST"])
def send_change_heading_name():
    heading_id = request.form["heading_id"]
    new_name = request.form["new_heading"]
    if new_name != "":
        dbf.update_heading(new_name, heading_id)
    return redirect("/settings/headings")

@app.route("/settings/heading_order/send", methods=["POST"])
def send_heading_order():
    heading_order = request.form.getlist("heading_order")
    heading_ids = request.form.getlist("heading_id")
    dbf.update_order_index(heading_order, heading_ids, "heading")
    return redirect("/settings/headings")

@app.route("/settings/delete_heading/send", methods=["POST"])
def send_delete_heading():
    pass

@app.route("/new_subforum/send", methods=["POST"])
def send_subforum():
    subforum = request.form["new_subforum"]
    heading = request.form["heading"]
    dbf.new_subforum(subforum, heading)
    return redirect("/settings/subforums")

@app.route("/settings/subforum_rename/send", methods=["POST"])
def rename_subforum():
    subforum_id = request.form["old_name"]
    name = request.form["new_name"]
    if name != "":
        dbf.update_subforum_name(name, subforum_id)
    return redirect("/settings/subforums")

@app.route("/settings/subforum_order/send", methods=["POST"])
def update_subforum_order():
    subforum_order = request.form.getlist("subforum_order")
    subforum_ids = request.form.getlist("subforum_id")
    update_order_index(subforum_order, subforum_ids, "subforum")
    return redirect("/settings/subforums")
