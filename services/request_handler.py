from services import users as users
from services import database_functions as dbf
from services import help_functions as help


def forum_start(request):
    title = request.form.get("title")
    if title == "":
        return "Foorumin nimi on pakollinen tieto"
    subtitle = request.form.get("subtitle")
    if subtitle == "":
        subtitle = " "
    username = request.form.get("username")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    error_message = users.before_register(username, password1, password2)
    if not error_message:
        hash_value = users.hash_password(password1)
        if dbf.forum_setup(username, hash_value, title, subtitle):
            users.create_session(username)
        else:
            error_message = "Tapahtui virhe, yritä uudelleen"
    return error_message


# NEW

def new_heading(request):
    heading_name = request.form.get("heading")
    if help.check_input(heading_name, 1, 60):
        return dbf.new_heading(heading_name)
    return "Otsikon pituus 1-60 merkkiä."

def new_subforum(request):
    subforum_name = request.form.get("new_subforum")
    heading_id = request.form.get("heading")
    if help.check_input(subforum_name, 1, 60):
        return dbf.new_subforum(subforum_name, heading_id)
    return "Subforumin nimen pituus 1-60 merkkiä."

def new_topic(request, subforum_id, username):
    title = request.form.get("title")
    message = request.form.get("content")
    if help.check_input(title, 1, 100) and help.check_input(message, 1, 5000):
        return dbf.new_topic(title, message, subforum_id, username) #returns topic_id
    return None

def new_message(request, topic_id, username):
    message = request.form.get("message")
    if help.check_input(message, 1, 5000) and not dbf.topic_locked(topic_id):
        return dbf.new_message(topic_id, message, username)
    return "Viestin pituus ei sallituissa rajoissa."


# UPDATE

def update_title(request):
    title = request.form.get("title")
    if not help.check_input(title, 1, 35):
        return "Foorumumin nimen täytyy olla 1-35 merkkiä."
    if not dbf.update_title(title, 1):
       return "Virhe nimen tallennuksessa."
    subtitle = request.form.get("subtitle")
    if subtitle == "":
        subtitle = " "
    if not help.check_input(subtitle, 0, 50):
        return "Foorumumin alaotsikon maksimipituus on 50 merkkiä."
    if not dbf.update_title(subtitle, 2):
        return "Virhe nimen tallennuksessa."
    return ""


def change_heading(request):
    heading_id = request.form.get("heading_id")
    new_name = request.form.get("new_heading")
    if help.check_input(new_name, 1, 60):
        return dbf.update_heading(new_name, heading_id)
    return "Otsikon pituus 1-60 merkkiä."

def heading_order(request):
    heading_order = request.form.getlist("heading_order")
    heading_ids = request.form.getlist("heading_id")
    return dbf.update_order_index(heading_order, heading_ids, "heading")

def rename_subforum(request):
    subforum_id = request.form.get("old_name")
    name = request.form.get("new_name")
    if help.check_input(name, 1, 60):
        return dbf.update_subforum_name(name, subforum_id)
    return "Subforumin nimen pituus 1-60 merkkiä."

def update_subforum_order(request):
    subforum_order = request.form.getlist("subforum_order")
    subforum_ids = request.form.getlist("subforum_id")
    return dbf.update_order_index(subforum_order, subforum_ids, "subforum")
    
def subforum_move(request):
    subforum_id = request.form.get("relocated_subforum")
    heading_id = request.form.get("new_heading")
    return dbf.subforum_move(subforum_id, heading_id)

def update_topic(request, topic_id):
    topic_name = request.form.get("topic_name")
    if not help.check_input(topic_name, 1, 100):
        return "Otsikon pituus 1-100 merkkiä"
    pinned = request.form.get("pinned")
    locked = request.form.get("locked")
    visibility = request.form.get("visibility")
    subforum_id = request.form.get("subforum_id")
    return dbf.update_topic(topic_name, pinned, locked, visibility, topic_id, subforum_id)

def edit_message(request):
    message = request.form.get("message")
    message_id = request.form.get("message_id")
    sender, topic_id = dbf.message_sender_and_topic(message_id)
    if not users.check_credentials(sender):
        return ("Ei oikeutta tehdä muutoksia.", message_id, topic_id)
    if not help.check_input(message, 1, 5000):
        return ("Viestin pituus ei sallituissa rajoissa.", message_id, topic_id)
    return (dbf.update_message(message, message_id), message_id, topic_id)


# USERS

def register_user(request):
    username = request.form.get("username")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    error = users.before_register(username, password1, password2)
    if not error:
        error = users.register_user(username, password1)
    return error

def login(request):
    username = request.form.get("username")
    password = request.form.get("password")
    hash_value = dbf.fetch_password(username)
    if not hash_value:
        return False
    if users.check_password(hash_value, password):
        users.create_session(username)
        return True
    return False

def new_admin(request):
    user_id = request.form.get("user_id")
    if user_id == "":
        return "Kohdetta ei valittu."
    return dbf.new_admin(user_id)

def remove_admin(request):
    user_id = request.form.get("user_id")
    if user_id == "":
        return "Kohdetta ei valittu."
    return dbf.remove_admin(user_id)


# SEARCH

def search_handler(request):
    word = request.args.get("word", "")
    keyword = help.check_asterisk(word)
    sender = request.args.get("sender", "")
    sender = help.check_asterisk(sender)
    subforums = request.args.getlist("subforum")
    subforums = [int(x) for x in subforums]
    time = request.args.get("time", "")
    order = request.args.get("order", "DESC")
    visibility = users.get_visibility()
    return dbf.search(keyword, sender, subforums, time, order, visibility), word

def search_from_topic(request, topic_id):
    word = request.args.get("query")
    keyword = help.check_asterisk(word)
    return dbf.search_from_topic(keyword, topic_id), word


# DELETE

def delete_topics_messages(request):
    message_id = request.form.get("delete_message")
    topic_id = request.form.get("delete_topic")
    if message_id:
        return ("topic", dbf.delete_message(int(message_id)))
    if topic_id:
        return ("subforum", dbf.delete_topic(int(topic_id)))
    return (None, None)

def delete_heading(request):
    delete_id = request.form.get("heading_id_delete")
    transfer_id = request.form.get("heading_id_transfer")
    if delete_id == "":
        return "Kohdetta ei valittu."
    if delete_id == transfer_id:
        return "Poistettava otsikko sama kuin siirtokohde."
    return dbf.delete_heading(delete_id, transfer_id)

def delete_subforum(request):
    delete_id = request.form.get("subforum_id_delete")
    if delete_id == "":
        return "Kohdetta ei valittu."
    return dbf.delete_subforum(delete_id)


    
