'''coderadi'''

# ? Importing libraries
from flask import Flask, redirect, url_for, flash
from dotenv import load_dotenv
import os
from extensions import *

# ? Importing routers
from routers.router import router
from routers.api import api
from routers.auth import auth
from routers.project import project
from routers.team import team
from routers.docs import docs
from routers.app import app

# ! Loading environment variables
load_dotenv('.venv/vars.env')

# ! Building server
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
server.config['SQLALCHEMY_TRACK_MODIFIACTIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFIACTIONS')
server.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
server.wsgi_app = ProxyFix(server.wsgi_app, x_proto=1, x_host=1)

# ! Binding extensions
bind_extensions(server)
init_oauth(server)

# ! Binding routers
server.register_blueprint(router)
server.register_blueprint(api)
server.register_blueprint(auth)
server.register_blueprint(project)
server.register_blueprint(team)
server.register_blueprint(docs)
server.register_blueprint(app)

# * 401 error handler
@server.errorhandler(401)
def unauthorized_(error):
    flash("Login required", "warning")
    return redirect(url_for('auth.signup'))