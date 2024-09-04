from flask import Blueprint, redirect, render_template, request #, url_for
import database_functions as dbf

settings_bp = Blueprint('settings', __name__)


# SETTINGS
@settings_bp.route("/")
def settings():
    forum_name = dbf.fetch_title()
    if users.is_admin():
        titles = dbf.fetch_title()
        return render_template("settings.html", titles=titles, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")

@settings_bp.route("/headings")
def heading_settings():
    forum_name = dbf.fetch_title()
    if users.is_admin():        
        headings = dbf.fetch_headings()
        return render_template("heading_settings.html", headings=headings, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")

@settings_bp.route("/subforums")
def subforums():
    forum_name = dbf.fetch_title()
    if users.is_admin():
        headings = dbf.fetch_headings()
        subforums_list = dbf.subforum_list()
        headings_and_subforums = dbf.headings_and_subforums2()
        return render_template("subforum_settings.html", headings=headings, subforums_list=subforums_list, headings_and_subforums=headings_and_subforums, forum_name=forum_name)
    return render_template("error.html", forum_name=forum_name, error="Ei oikeutta nähdä sivua.")


## Settings send
@settings_bp.route("/send", methods=["POST"])
def send_settings():
    title = request.form["title"]
    if title != "":
        dbf.new_title(title)
    subtitle = request.form["subtitle"]
    if subtitle != "":
        dbf.new_subtitle(subtitle)
    else:
        pass
        # POISTA ALAOTSIKKO
    return redirect("/")

@settings_bp.route("/heading_name/send", methods=["POST"])
def send_new_heading():
    heading_name = request.form["heading"]
    if heading_name != "":
        dbf.new_heading(heading_name)
    return redirect("/settings/headings")

@settings_bp.route("/heading_rename/send", methods=["POST"])
def send_change_heading_name():
    heading_id = request.form["heading_id"]
    new_name = request.form["new_heading"]
    if new_name != "":
        dbf.update_heading(new_name, heading_id)
    return redirect("/settings/headings")

@settings_bp.route("/heading_order/send", methods=["POST"])
def send_heading_order():
    heading_order = request.form.getlist("heading_order")
    heading_ids = request.form.getlist("heading_id")
    dbf.update_order_index(heading_order, heading_ids, "heading")
    return redirect("/settings/headings")

@settings_bp.route("/delete_heading/send", methods=["POST"])
def send_delete_heading():
    pass

@settings_bp.route("/new_subforum/send", methods=["POST"])
def send_subforum():
    subforum = request.form["new_subforum"]
    heading = request.form["heading"]
    dbf.new_subforum(subforum, heading)
    return redirect("/settings/subforums")

@settings_bp.route("/subforum_rename/send", methods=["POST"])
def rename_subforum():
    subforum_id = request.form["old_name"]
    name = request.form["new_name"]
    if name != "":
        dbf.update_subforum_name(name, subforum_id)
    return redirect("/settings/subforums")

@settings_bp.route("/subforum_order/send", methods=["POST"])
def update_subforum_order():
    subforum_order = request.form.getlist("subforum_order")
    subforum_ids = request.form.getlist("subforum_id")
    dbf.update_order_index(subforum_order, subforum_ids, "subforum")
    return redirect("/settings/subforums")