import users
import database_functions as dbf


# REQUEST HANDLERS

def forum_start(request):
    title = request.form["title"]
    subtitle = request.form["subtitle"]
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if title == "":
        error_message = "Foorumin nimi on pakollinen tieto"
        return error_message
    error_message = users.forum_setup(username, password1, password2, title, subtitle)
    return error_message

def update_topic(request, topic_id):
    topic_name = request.form["topic_name"]
    if not check_input(topic_name, 1, 100):
        return "Otsikon pituus 1-100 merkkiä"
    pinned = request.form["pinned"]
    locked = request.form["locked"]
    visibility = request.form["visibility"]
    subforum_id = request.form["subforum_id"]
    error_message = dbf.update_topic(topic_name, pinned, locked, visibility, topic_id, subforum_id)
    return error_message

def delete_topic(request):
    topic_id = int(request.form["delete"])
    subforum_id = dbf.delete_topic(topic_id)
    return subforum_id

def new_message(request, topic_id):
    message = request.form["message"]
    username = users.get_username()
    if check_input(message, 1, 5000) and not dbf.topic_locked(topic_id):
        error = dbf.new_message(topic_id, message, username)
        return error
    error = "Viestin pituus ei sallituissa rajoissa."
    return error
        

#SEARCH

def search_handler(request):
    word = request.args.get("word", "")
    word = check_asterisk(word)
    sender = request.args.get("sender", "")
    sender = check_asterisk(sender)
    subforums = request.args.getlist("subforum")
    subforums = [int(x) for x in subforums]
    time = request.args.get("time", "")
    order = request.args.get("order", "DESC")
    messages = dbf.search(word, sender, subforums, time, order)
    return messages


# CHECK INPUT

def check_input(content: str, min: int, max:int):
    if min <= len(content) <= max:
        return True
    return False

def check_asterisk(keyword):
    if keyword:
        if keyword[-1] == "*":
            keyword = keyword[0:-1]
        else:
            keyword =(r"([\.\,!\?\"\'\(\)=\-:;\+/\s]|^)" + keyword + r"([\.\,!\?\"\'\(\)=\-:;\+/\s]|$)")
    return keyword


    