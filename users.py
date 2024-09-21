from werkzeug.security import check_password_hash, generate_password_hash
from flask import session
import database_functions as dbf
import help_functions as help



# LOGIN, REGISTER

def register_user(username, password1):
    hash_value = hash_password(password1)
    if dbf.register_user(username, hash_value):
        create_session(username)
        return ""
    else:
        return "Virhe tiedon tallentamisessa."

def before_register(username, password1, password2):
    if username == "" or password1 == "" or password2 == "":
        return "Pakollisia tietoja puuttuu"
    if not help.check_input(username, 1, 25):
        return "Käyttäjätunnuksen pituus 1-25 merkkiä."
    if dbf.check_username(username):
        return "Valittu käyttäjätunnus on jo käytössä"
    if not help.check_input(password1, 8, 15):
        return "Salasanan pituus 8-15 merkkiä."
    if password1 != password2:
        return "Salasanat eivät täsmää"
    return ""

def hash_password(password):
    return generate_password_hash(password)


# CHECK

def check_credentials(username):
    if is_admin():
        return True
    return username == get_username()

def check_password(hash_value, password):
    return check_password_hash(hash_value, password)


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

