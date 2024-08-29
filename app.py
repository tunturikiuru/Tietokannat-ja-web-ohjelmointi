from flask import Flask
from flask import redirect, render_template, request, url_for, session
#from werkzeug.security import generate_password_hash
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import database_functions as dbf
import users
import help_functions as help

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        forum_name = dbf.fetch_title()
        if forum_name[0] == "":
            return render_template("start.html")
        else:
            subforum_order = dbf.index_page()
            return render_template("index.html", forum_name=forum_name, subforum_order=subforum_order)
    if request.method == "POST":
        error_message = help.forum_start(request)
        if error_message:
            return render_template("start.html", error_message=error_message)
        else:
            return redirect("/settings")

@app.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    forum_name = dbf.fetch_title()
    subforum = dbf.fetch_subforum_by_id(subforum_id)
    topics = dbf.subforum_page(subforum_id)
    return render_template("subforum.html", subforum=subforum, topics=topics, forum_name=forum_name)

@app.route("/subforum/<int:id>/new_topic")
def create_new_topic(id):
    forum_name = dbf.fetch_title()
    subforum = dbf.fetch_subforum_by_id(id)
    return render_template("new_topic.html", subforum=subforum, forum_name=forum_name)

@app.route("/subforum/<int:subforum_id>/new_topic/send", methods=["POST"])
def send_new_topic(subforum_id):
    username = users.get_username()
    forum_name = dbf.fetch_title()
    if username:
        title = request.form["title"]
        message = request.form["content"]
        if help.check_input(title, 1, 100) and help.check_input(message, 1, 5000):
            topic_id = dbf.new_topic(title, message, subforum_id, username)
            return redirect(url_for("topic", topic_id = topic_id))
        return render_template("error.html", forum_name = forum_name, error = "Otsikon tai viestin pituus ei sallituissa rajoissa")
    else:
        if users.login(request):
            return redirect(url_for("create_new_topic", id=subforum_id))
        return render_template("error.html", forum_name=forum_name, error = "Väärä käyttäjätunnus tai salasana")

@app.route("/topic/<int:topic_id>")
def topic(topic_id):
    forum_name = dbf.fetch_title()
    subforum = dbf.fetch_subforum_by_topic(topic_id)
    topic = dbf.fetch_topic(topic_id)
    messages = dbf.topic_page(topic_id)
    return render_template("topic.html", messages=messages, subforum=subforum, topic=topic, forum_name=forum_name)

@app.route("/topic/<int:topic_id>/send", methods=["POST"])
def send_new_message(topic_id):
    forum_name = dbf.fetch_title()
    username = users.get_username()
    if username:
        message = request.form["message"]
        if help.check_input(message, 1, 5000):
            dbf.new_message(topic_id, message, username)
            return redirect(url_for("topic", topic_id=topic_id))
        return render_template("error.html", forum_name=forum_name, error = "Viestin pituus ei sallituissa rajoissa.")
    else:
        if users.login(request):
            return redirect(url_for("create_new_message", topic_id=topic_id))
        return render_template("error.html", forum_name=forum_name, error = "Väärä käyttäjätunnus tai salasana.")

#USERS
@app.route("/register", methods=["GET", "POST"])
def register():
    forum_name = dbf.fetch_title()
    if request.method == "GET":
        return render_template("register.html", forum_name=forum_name)
    if request.method == "POST":
        error_message = users.register_user(request)
        if error_message:
            return render_template("register.html", message=error_message, forum_name=forum_name)
        else:
            return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    forum_name = dbf.fetch_title()
    if request.method == "GET":
        return render_template("login.html", forum_name=forum_name)
    if request.method == "POST":
        if users.login(request):
            return redirect("/")
    return render_template("login.html", message="Väärä käyttäjätunnus tai salasana", forum_name=forum_name)
    
@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")


#SEARCH

@app.route("/search")
def search():
    forum_name = dbf.fetch_title()
    subforums = dbf.subforum_list()
    return render_template("search.html", forum_name=forum_name, subforums=subforums)

@app.route("/search/result")
def search_result():
    forum_name = dbf.fetch_title()
    messages = help.search_handler(request)
    return render_template("result.html", messages=messages, forum_name=forum_name)

@app.route("/topic/<int:topic_id>/result")
def search_from_topic(topic_id):
    forum_name = dbf.fetch_title()
    word = request.args["query"]
    word = help.check_asterisk(word)
    messages = dbf.search_from_topic(word, topic_id)
    return render_template("result.html", messages=messages, forum_name=forum_name)

@app.route("/subforum/<int:subforum_id>/result")
def search_from_subforum(subforum_id):
    forum_name = dbf.fetch_title()
    messages = help.search_handler(request)
    return render_template("result.html", messages=messages, forum_name=forum_name)


# SETTINGS
@app.route("/settings")
def settings():
    forum_name = dbf.fetch_title()
    if users.is_admin():
        titles = dbf.fetch_title()
        return render_template("settings.html", titles=titles, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")

@app.route("/settings/headings")
def heading_settings():
    forum_name = dbf.fetch_title()
    if users.is_admin():        
        headings = dbf.fetch_headings()
        return render_template("heading_settings.html", headings=headings, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")

@app.route("/settings/subforums")
def subforums():
    forum_name = dbf.fetch_title()
    if users.is_admin():
        headings = dbf.fetch_headings()
        subforums_list = dbf.subforum_list()
        headings_and_subforums = dbf.headings_and_subforums2()
        return render_template("subforum_settings.html", headings=headings, subforums_list=subforums_list, headings_and_subforums=headings_and_subforums, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")


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

@app.route("/settings/new_subforum/send", methods=["POST"])
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
    dbf.update_order_index(subforum_order, subforum_ids, "subforum")
    return redirect("/settings/subforums")
