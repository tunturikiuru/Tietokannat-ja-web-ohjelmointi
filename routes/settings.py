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



# SETTINGS SEND

@settings_bp.route("/send", methods=["POST"])
def send_settings():
    forum_name = dbf.fetch_title()
    error = rh.update_title(request)
    if error:
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/heading_name/send", methods=["POST"])
def send_new_heading():
    forum_name = dbf.fetch_title()
    error = rh.new_heading(request)
    if error:
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings/")

@settings_bp.route("/heading_rename/send", methods=["POST"])
def send_change_heading():
    forum_name = dbf.fetch_title()
    error = rh.change_heading(request)
    if error:
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings/")

@settings_bp.route("/heading_order/send", methods=["POST"])
def send_heading_order():
    forum_name = dbf.fetch_title()
    error = rh.heading_order(request)
    if error:
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings/")

@settings_bp.route("/delete_heading/send", methods=["POST"])
def send_delete_heading():
    forum_name = dbf.fetch_title()
    error = rh.delete_heading(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings")

@settings_bp.route("/new_subforum/send", methods=["POST"])
def send_subforum():
    forum_name = dbf.fetch_title()
    error = rh.new_subforum(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
    return redirect("/settings/")

@settings_bp.route("/subforum_rename/send", methods=["POST"])
def rename_subforum():
    forum_name = dbf.fetch_title()
    error = rh.rename_subforum(request)
    if error: 
        return render_template("error.html", forum_name=forum_name, error=error)
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

