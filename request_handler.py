import users
import database_functions as dbf
import help_functions as help


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

def new_message(request, topic_id):
    message = request.form["message"]
    username = users.get_username()
    if help.check_input(message, 1, 5000) and not dbf.topic_locked(topic_id):
        error = dbf.new_message(topic_id, message, username)
        return error
    error = "Viestin pituus ei sallituissa rajoissa."
    return error


# UPDATE

def update_title(request):
    title = request.form.get("title")
    if not help.check_input(title, 1, 35):
        return "Foorumumin nimen täytyy olla 1-35 merkkiä."
    error = dbf.update_title(title, 1)
    if error: 
        return error
    subtitle = request.form.get("subtitle")
    if subtitle == "":
        subtitle = " "
    if not help.check_input(subtitle, 0, 50):
        return "Foorumumin alaotsikon maksimipituus on 50 merkkiä."
    error = dbf.update_title(subtitle, 2)
    return error

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
    dbf.update_order_index(subforum_order, subforum_ids, "subforum")
    
def subforum_move(request):
    subforum_id = request.form.get("relocated_subforum")
    heading_id = request.form.get("new_heading")
    error = dbf.subforum_move(subforum_id, heading_id)
    return error

def update_topic(request, topic_id):
    topic_name = request.form["topic_name"]
    if not help.check_input(topic_name, 1, 100):
        return "Otsikon pituus 1-100 merkkiä"
    pinned = request.form["pinned"]
    locked = request.form["locked"]
    visibility = request.form["visibility"]
    subforum_id = request.form["subforum_id"]
    error_message = dbf.update_topic(topic_name, pinned, locked, visibility, topic_id, subforum_id)
    return error_message

def edit_message(request):
    message = request.form["message"]
    message_id = request.form["message_id"]
    sender, topic_id = dbf.message_sender_and_topic(message_id)
    if not users.check_credentials(sender):
        return ("Ei oikeutta tehdä muutoksia.", message_id, topic_id)
    if not help.check_input(message, 1, 5000):
        return ("Viestin pituus ei sallituissa rajoissa.", message_id, topic_id)
    return (dbf.update_message(message, message_id), message_id, topic_id)


# USERS

def new_admin(request):
    user_id = request.form.get("user_id")
    if user_id == "":
        return "Kohdetta ei valittu."
    error = dbf.new_admin(user_id)
    return error

def remove_admin(request):
    user_id = request.form.get("user_id")
    if user_id == "":
        return "Kohdetta ei valittu."
    error = dbf.remove_admin(user_id)
    return error


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


    
