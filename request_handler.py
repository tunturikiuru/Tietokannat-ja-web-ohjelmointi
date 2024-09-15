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

def new_message(request, topic_id):
    message = request.form["message"]
    username = users.get_username()
    if help.check_input(message, 1, 5000) and not dbf.topic_locked(topic_id):
        error = dbf.new_message(topic_id, message, username)
        return error
    error = "Viestin pituus ei sallituissa rajoissa."
    return error

def edit_message(request):
    message = request.form["message"]
    message_id = request.form["message_id"]
    sender, topic_id = dbf.message_sender_and_topic(message_id)
    if not users.check_credentials(sender):
        return ("Ei oikeutta tehdä muutoksia.", message_id, topic_id)
    if not help.check_input(message, 1, 5000):
        return ("Viestin pituus ei sallituissa rajoissa.", message_id, topic_id)
    return (dbf.update_message(message, message_id), message_id, topic_id)


# UPDATE

def update_subforum_order(request): #KESKEN
    subforum_order = request.form.getlist("subforum_order")
    print(subforum_order)
    subforum_ids = request.form.getlist("subforum_id")
    print(subforum_order)
    dbf.update_order_index(subforum_order, subforum_ids, "subforum")
    
def subforum_move(request):
    subforum_id = request.form.get("relocated_subforum")
    heading_id = request.form.get("new_heading")
    error = dbf.subforum_move(subforum_id, heading_id)
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
    if delete_id == transfer_id:
        return "Poistettava otsikko sama kuin siirtokohde."
    return dbf.delete_heading(delete_id, transfer_id)

def delete_subforum(request):
    delete_id = request.form.get("subforum_id_delete")
    if delete_id == "":
        return "Kohdetta ei valittu."
    return dbf.delete_subforum(delete_id)


    
