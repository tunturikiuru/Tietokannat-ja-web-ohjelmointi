from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost"
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute(text("SELECT name, subtitle FROM forums"))
    forums = result.fetchall()
    return render_template("index.html", forums=forums) 

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/send", methods=["POST"])
def send():
    name = request.form["title"]
    subtitle = request.form["subtitle"]
    alias = request.form["alias"]
    sql = "INSERT INTO forums (name, subtitle, alias) VALUES (:name, :subtitle, :alias)"
    db.session.execute(text(sql), {"name":name, "subtitle":subtitle, "alias":alias})
    db.session.commit()
    return redirect("/")