from werkzeug.security import check_password_hash, generate_password_hash
import database_functions as dbf
from flask import session


#LOGIN VIRHEILMOITUS
def login(username, password):
    print(password)
    hash_value = dbf.fetch_password(username)
    print(hash_value)
    if not hash_value:
        return False
    if check_password_hash(hash_value, password):
        session["username"] = username
        return True
    return False

def logout():
    del session["username"]

def register_user(username, password1, password2):
    if dbf.check_username(username):
        return "Valittu käyttäjätunnus on jo käytössä"
    if password1 != password2:
        return "Salasanat eivät täsmää"
    hash_value = generate_password_hash(password1)
    if dbf.register_user(username, hash_value):
        session["username"] = username
        return ""
    return "Tapahtui virhe, yritä uudelleen"