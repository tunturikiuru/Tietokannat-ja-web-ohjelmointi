from flask import Flask
from os import getenv
from db import db

def create_app():
    app = Flask(__name__)
    app.secret_key = getenv("SECRET_KEY")

    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    db.init_app(app)

    from routes.settings import settings_bp
    from routes.general import general_bp

    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(general_bp)

    return app

app = create_app()
