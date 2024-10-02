from flask import Blueprint, redirect, render_template, request, url_for
from services import database_functions as dbf
from services import users as users
from services import request_handler as rh

general_bp = Blueprint("general", __name__)


@general_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        forum_name = dbf.fetch_title()
        if not forum_name:
            return render_template("start.html")
        else:
            subforum_order = dbf.index_page()
            return render_template("index.html", forum_name=forum_name, subforum_order=subforum_order)
    if request.method == "POST":
        error_message = rh.forum_start(request)
        if error_message:
            return render_template("start.html", error_message=error_message)
        else:
            return redirect("/settings")

@general_bp.route("/subforum/<int:subforum_id>")
def subforum(subforum_id):
    forum_name = dbf.fetch_title()
    subforum = dbf.fetch_subforum_by_id(subforum_id)
    topics = dbf.subforum_page(subforum_id)
    return render_template("subforum.html", subforum=subforum, topics=topics, forum_name=forum_name)

@general_bp.route("/subforum/<int:id>/new_topic")
def create_new_topic(id):
    forum_name = dbf.fetch_title()
    subforum = dbf.fetch_subforum_by_id(id)
    return render_template("new_topic.html", subforum=subforum, forum_name=forum_name)

@general_bp.route("/subforum/<int:subforum_id>/new_topic/send", methods=["POST"])
def send_new_topic(subforum_id):
    forum_name = dbf.fetch_title()
    username = users.get_username()
    if username:
        topic_id = rh.new_topic(request, subforum_id, username)
        if topic_id:
            return redirect(url_for("general.topic", topic_id = topic_id))
        return render_template("error.html", forum_name = forum_name, error = "Otsikon tai viestin pituus ei sallituissa rajoissa")
    else:
        if rh.login(request):
            return redirect(url_for("general.create_new_topic", id=subforum_id))
        return render_template("error.html", forum_name=forum_name, error = "Väärä käyttäjätunnus tai salasana")

@general_bp.route("/topic/<int:topic_id>")
def topic(topic_id):
    forum_name = dbf.fetch_title()
    path = dbf.path_to_topic(topic_id)
    messages = dbf.topic_page(topic_id)
    return render_template("topic.html", messages=messages, path=path, forum_name=forum_name)

@general_bp.route("/topic/<int:topic_id>/message/<int:message_id>")
def jump_to_message(topic_id, message_id):
    return redirect(url_for("general.topic", topic_id=topic_id) + f'#{topic_id}-{message_id}')

@general_bp.route("/topic/<int:topic_id>/send", methods=["POST"])
def send_new_message(topic_id):
    forum_name = dbf.fetch_title()
    username = users.get_username()
    error = ""
    if username:
        error = rh.new_message(request, topic_id, username)
        if not error:
            return redirect(url_for("general.topic", topic_id=topic_id))
    else:
        if users.login(request):
            return redirect(url_for("general.create_new_message", topic_id=topic_id))
        error = "Väärä käyttäjätunnus tai salasana."
    return render_template("error.html", forum_name=forum_name, error = error)


# EDIT

@general_bp.route("/topic/<int:topic_id>/edit")
def edit_topic(topic_id):
    forum_name = dbf.fetch_title()
    if users.is_admin():
        subforum_list = dbf.subforum_list()
        topic = dbf.fetch_topic_data(topic_id)
        return render_template("edit_topic.html", forum_name=forum_name, topic=topic, subforum_list=subforum_list)
    return render_template("error.html", forum_name=forum_name, error = "Ei oikeutta nähdä sivua.")

@general_bp.route("/topic/<int:topic_id>/edit/send", methods=["POST"])
def edit_topic_send(topic_id):
    forum_name = dbf.fetch_title()
    error = "Ei oikeutta pyyntöön."
    if users.is_admin():
        error = rh.update_topic(request, topic_id)
        if not error:
            subforum_id = dbf.subforum_id(topic_id)
            return redirect(url_for("general.subforum", subforum_id=subforum_id))
    return render_template("error.html", forum_name=forum_name, error=error)

@general_bp.route("/edit/message/<int:message_id>")
def edit_message(message_id):
    forum_name = dbf.fetch_title()
    message = dbf.fetch_message(message_id)
    if users.get_username() == message.sender or users.is_admin():
        return render_template("edit_message.html", forum_name=forum_name, message=message)
    return render_template("error.html", forum_name=forum_name, error = "Ei oikeutta tehdä muutoksia.")

@general_bp.route("/edit/message/send", methods=["POST"])
def edit_message_send():
    forum_name = dbf.fetch_title()
    error, message_id, topic_id = rh.edit_message(request)
    if not error:
        return redirect(url_for("general.jump_to_message", topic_id=topic_id, message_id=message_id))
    return render_template("error.html", forum_name=forum_name, error = error)


# DELETE

@general_bp.route("/delete/topics_and_messages", methods=["POST"])
def delete_topics_messages():
    forum_name = dbf.fetch_title()
    error = "Ei oikeutta pyyntöön."
    if users.is_admin():
        target, id = rh.delete_topics_messages(request)
        if id and target == "topic":
            return redirect(url_for("general.topic", topic_id=id))
        if id and target == "subforum":
            return redirect(url_for("general.subforum", subforum_id=id))
        error = "Tapahtui virhe."
    return render_template("error.html", forum_name=forum_name, error=error)


#USERS

@general_bp.route("/register", methods=["GET", "POST"])
def register():
    forum_name = dbf.fetch_title()
    if request.method == "GET":
        return render_template("register.html", forum_name=forum_name)
    if request.method == "POST":
        error = rh.register_user(request)
        if error:
            return render_template("register.html", message=error, forum_name=forum_name)
        else:
            return redirect("/")

@general_bp.route("/login", methods=["GET", "POST"])
def login():
    forum_name = dbf.fetch_title()
    if request.method == "GET":
        return render_template("login.html", forum_name=forum_name)
    if request.method == "POST":
        if rh.login(request):
            return redirect("/")
        return render_template("login.html", message="Väärä käyttäjätunnus tai salasana", forum_name=forum_name)
    
@general_bp.route("/logout")
def logout():
    users.logout()
    return redirect("/")


#SEARCH

@general_bp.route("/search")
def search():
    forum_name = dbf.fetch_title()
    subforums = dbf.subforum_list()
    return render_template("search.html", forum_name=forum_name, subforums=subforums)

@general_bp.route("/search/result")
def search_result():
    forum_name = dbf.fetch_title()
    messages, word = rh.search_handler(request)
    return render_template("result.html", messages=messages, forum_name=forum_name, word=word)

@general_bp.route("/topic/<int:topic_id>/result")
def search_from_topic(topic_id):
    forum_name = dbf.fetch_title()
    messages, word = rh.search_from_topic(request, topic_id)
    return render_template("result.html", messages=messages, forum_name=forum_name, word=word)

@general_bp.route("/subforum/<int:subforum_id>/result")
def search_from_subforum(subforum_id):
    forum_name = dbf.fetch_title()
    messages, word = rh.search_handler(request)
    return render_template("result.html", messages=messages, forum_name=forum_name, word=word)