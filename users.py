from werkzeug.security import check_password_hash, generate_password_hash
import database_functions as dbf
from flask import session


def forum_setup(username, password1, password2, title, subtitle=None):
    error_message = before_register(username, password1, password2)
    if not error_message:
        hash_value = hash_password(password1)
        if dbf.forum_setup(username, hash_value, title, subtitle):
            create_session(username)
        else:
            error_message = "Tapahtui virhe, yritä uudelleen"
    return error_message

def login(username, password):
    hash_value = dbf.fetch_password(username)
    if not hash_value:
        return False
    if check_password_hash(hash_value, password):
        create_session(username)
        return True
    return False

def logout():
    session.clear()

def register_user(username, password1, password2):
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

"""def is_user():
    pass"""

def is_admin():
    return session.get("role") == "admin"

def create_session(username):
    session["username"] = username
    if dbf.is_admin(username):
        session["role"] = 'admin'
    else:
        session["role"] = 'user'

    
