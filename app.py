from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, abort, make_response, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import sqlite3
import os
# from backend.models import *
from backend.controllers import *
from flask_bcrypt import Bcrypt

app = None #initially none

def init_app():
    app = Flask(__name__) #object of Flask
    app.config["SECRET_KEY"] = "secret"
    from backend.controllers import controllers
    # from backend.authentication import authentication

    #this part should be running after the Database is created

    login_manager = LoginManager()
    login_manager.login_view = 'controllers.user_login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    app.register_blueprint(controllers, url_prefix="/")
    # app.register_blueprint(authentication, url_prefix="/")
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///TFI.sqlite3"
    app.app_context().push() #Direct access app by other modules(db, authentication)
    db.init_app(app) #object.method(<parameter>)
    # api.init_app(app)
    

    print("Application has started....")
    return app

    # from backend.models import *
    # from app import *
    # db.create_all()

app = init_app()
from backend.controllers import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()