from werkzeug.security import check_password_hash, generate_password_hash
import database_functions as dbf
from flask import session


# FIRST ADMIN
def forum_setup(username, password1, password2, title, subtitle=None):
    error_message = before_register(username, password1, password2)
    if not error_message:
        hash_value = hash_password(password1)
        if dbf.forum_setup(username, hash_value, title, subtitle):
            create_session(username)
        else:
            error_message = "Tapahtui virhe, yritä uudelleen"
    return error_message


# LOGIN, REGISTER
def login(request):
    username = request.form["username"]
    password = request.form["password"]
    hash_value = dbf.fetch_password(username)
    if not hash_value:
        return False
    if check_password_hash(hash_value, password):
        create_session(username)
        return True
    return False

def register_user(request):
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    error_message = before_register(username, password1, password2)
    if not error_message:
        hash_value = hash_password(password1)
        if dbf.register_user(username, hash_value):
            create_session(username)
        else:
            error_message = "Tapahtui virhe, yritä uudelleen"
    return error_message

def before_register(username, password1, password2):
    if username == "" or password1 == "" or password2 == "":
        return "Pakollisia tietoja puuttuu"
    if dbf.check_username(username):
        return "Valittu käyttäjätunnus on jo käytössä"
    if password1 != password2:
        return "Salasanat eivät täsmää"
    return ""

def hash_password(password):
    return generate_password_hash(password)


# SESSION
def create_session(username):
    session["username"] = username
    if dbf.is_admin(username):
        session["role"] = 'admin'
    else:
        session["role"] = 'user'

def logout():
    session.clear()

def is_admin():
    return session.get("role") == "admin"

def get_username():
    return session.get('username')



    
