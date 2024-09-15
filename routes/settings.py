from flask import Blueprint, redirect, render_template, request #, url_for
import database_functions as dbf
import users
import request_handler as rh
import help_functions as help

settings_bp = Blueprint('settings', __name__)



@settings_bp.before_request
def before_request():
    if not users.is_admin():
        forum_name = dbf.fetch_title()
        return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")


# SETTINGS
@settings_bp.route("/")
def settings():
    forum_name = dbf.fetch_title()
    forum_structure = dbf.get_forum_structure()
    return render_template("settings.html", forum_name=forum_name, forum_structure=forum_structure)

@settings_bp.route("/headings")
def heading_settings():
    forum_name = dbf.fetch_title()   
    headings = dbf.fetch_headings()
    return render_template("heading_settings.html", headings=headings, forum_name=forum_name)

@settings_bp.route("/subforums")
def subforums():
    forum_name = dbf.fetch_title()
    forum_structure = dbf.get_forum_structure()
    return render_template("subforum_settings.html", forum_structure=forum_structure, forum_name=forum_name)

@settings_bp.route("/admins")
def admins():
    forum_name = dbf.fetch_title()
    users = dbf.get_users()
    return render_template("admin.html", users=users, forum_name=forum_name)

@settings_bp.route("/users")
def user_settings():
    forum_name = dbf.fetch_title()
    users = dbf.get_users()
    print(users)
    return render_template("admin.html", users=users, forum_name=forum_name)


# SETTINGS SEND

@settings_bp.route("/send", methods=["POST"]) #ei tarkistettu
def send_settings():
    title = request.form["title"]
    if title == "":
        title = " "
    dbf.new_title(title)
    subtitle = request.form["subtitle"]
    if subtitle == "":
        subtitle = " "
    dbf.new_subtitle(subtitle)
    return redirect("/settings")

@settings_bp.route("/heading_name/send", methods=["POST"]) #ei tarkistettu
def send_new_heading():
    heading_name = request.form["heading"]
    if heading_name != "":
        dbf.new_heading(heading_name)
    return redirect("/settings/")

@settings_bp.route("/heading_rename/send", methods=["POST"]) #ei tarkistettu
def send_change_heading_name():
    heading_id = request.form["heading_id"]
    new_name = request.form["new_heading"]
    if new_name != "":
        dbf.update_heading(new_name, heading_id)
    return redirect("/settings/")

@settings_bp.route("/heading_order/send", methods=["POST"]) #ei tarkistettu
def send_heading_order():
    heading_order = request.form.getlist("heading_order")
    heading_ids = request.form.getlist("heading_id")
    dbf.update_order_index(heading_order, heading_ids, "heading")
    return redirect("/settings/")

@settings_bp.route("/delete_heading/send", methods=["POST"]) #ei tarkistettu
def send_delete_heading():
    forum_name = dbf.fetch_title()
    error = rh.delete_heading(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/new_subforum/send", methods=["POST"]) #ei tarkistettu
def send_subforum():
    subforum = request.form["new_subforum"]
    heading = request.form["heading"]
    dbf.new_subforum(subforum, heading)
    return redirect("/settings/")

@settings_bp.route("/subforum_rename/send", methods=["POST"]) #ei tarkistettu
def rename_subforum():
    subforum_id = request.form["old_name"]
    name = request.form["new_name"]
    if name != "":
        dbf.update_subforum_name(name, subforum_id)
    return redirect("/settings/")

@settings_bp.route("/subforum_move/send", methods=["POST"])
def move_subforum():
    forum_name = dbf.fetch_title()
    error = rh.subforum_move(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/subforum_order/send", methods=["POST"])
def update_subforum_order():
    forum_name = dbf.fetch_title()
    error = rh.update_subforum_order(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/subforum_delete", methods=["POST"])
def subforum_delete():
    forum_name = dbf.fetch_title()
    error = rh.delete_subforum(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/new_admin", methods=["POST"])
def new_admin():
    forum_name = dbf.fetch_title()
    error = rh.new_admin(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/remove_admin", methods=["POST"])
def remove_admin():
    forum_name = dbf.fetch_title()
    error = rh.remove_admin(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

