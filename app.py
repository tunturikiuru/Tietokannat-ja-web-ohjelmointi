from flask import Flask
from flask import redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost"
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute(text("SELECT heading_name FROM headings WHERE order_index < 3 ORDER BY order_index"))
    headings= result.fetchall()
    result = db.session.execute(text("SELECT h.order_index h_order, h.heading_name h_name, s.subforum_name s_name, s.subforum_id s_id FROM subforums s LEFT JOIN headings h ON h.heading_id = s. heading_id ORDER BY h.order_index, s.order_index"))
    subforums = result.fetchall()
    subforum_order = {}
    for subforum in subforums:
        if (subforum.h_order, subforum.h_name) not in subforum_order:
            subforum_order[(subforum.h_order, subforum.h_name)] = []
        subforum_order[(subforum.h_order, subforum.h_name)].append((subforum.s_name, subforum.s_id))
    return render_template("index.html", headings=headings, subforum_order=subforum_order) 

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/settings/send", methods=["POST"])
def send_settings():
    title = request.form["title"]
    if title != "":
        sql = "INSERT INTO headings (heading_name, order_index) VALUES (:title, 1) ON CONFLICT (order_index) DO UPDATE SET heading_name = :title"
        db.session.execute(text(sql), {"title":title})
        db.session.commit()
    subtitle = request.form["subtitle"]
    if subtitle != "":
        sql = "INSERT INTO headings (heading_name, order_index) VALUES (:subtitle, 2) ON CONFLICT (order_index) DO UPDATE SET heading_name = :subtitle"
        db.session.execute(text(sql), {"subtitle":subtitle})
        db.session.commit()
    private = request.form["private"]
    if private != "":
        sql = "INSERT INTO headings (heading_name, order_index) VALUES (:private, 3) ON CONFLICT (order_index) DO UPDATE SET heading_name = :private"
        db.session.execute(text(sql), {"private":private})
        db.session.commit()
    headings = request.form.getlist("heading")
    order_index = 4
    for heading in headings:
        if heading != "":
            sql = "INSERT INTO headings (heading_name, order_index) VALUES (:heading, :order_index) ON CONFLICT (order_index) DO UPDATE SET heading_name = :heading"
            db.session.execute(text(sql), {"heading":heading, "order_index":order_index})
            db.session.commit()
        order_index += 1
    return redirect("/")

@app.route("/new_subforum")
def new_subforum():
    sql = "SELECT heading_name, heading_id FROM headings WHERE order_index >= 3 ORDER BY order_index"
    result = db.session.execute(text(sql))
    headings = result.fetchall()
    return render_template("new_subforum.html", headings=headings)

@app.route("/subforum/send", methods=["POST"])
def send_subforum():
    subforum = request.form["subforum"]
    area = request.form["area"]
    sql = "INSERT INTO subforums (heading_id, subforum_name) VALUES (:area, :subforum)"
    db.session.execute(text(sql), {"area":area, "subforum":subforum})
    db.session.commit()
    return redirect("/")


