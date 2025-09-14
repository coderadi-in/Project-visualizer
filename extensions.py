'''coderadi'''

# ? Importing libraries
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from sqlalchemy import func

from werkzeug.security import (
    generate_password_hash as hashin,
    check_password_hash as hashout
)

from flask_login import (
    LoginManager, UserMixin, 
    login_user, logout_user, current_user, login_required, fresh_login_required
)

from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import time
import os

# ! Building extensions
db = SQLAlchemy()
logger = LoginManager()
migrate = Migrate()
socket = SocketIO()
oauth = OAuth()

# & Configure Google OAuth
def init_oauth(server):
    google = oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_ID'),
        client_secret=os.getenv('GOOGLE_SECRET'),
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v3/',
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account',
        },
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    )

    return google

# & function to bind all extensions to server
def bind_extensions(server):
    db.init_app(server)
    logger.init_app(server)
    migrate.init_app(server, db)
    socket.init_app(server)
    oauth.init_app(server)

# | User database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    googleid = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    bio = db.Column(db.Text(100), default="")
    pic = db.Column(db.String, default='/static/assets/icons/profile.png')
    password = db.Column(db.String(10))
    passkey = db.Column(db.String(6))

# | Project database model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, default="Untitled project")
    desc = db.Column(db.String(100))
    private = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    done = db.Column(db.Boolean, default=False)

# | Ojbective database model
class Objective(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String, nullable=False)
    doneby = db.Column(db.Integer, nullable=True)
    isdone = db.Column(db.Boolean, default=False)

# | Team database model
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, default="Untitled team")
    desc = db.Column(db.Text, default="")
    icon = db.Column(db.String, default="/static/public/default-team.png")
    members = db.Column(db.Integer, default=1)
    private = db.Column(db.Boolean, default=False)

# | Member database model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer, nullable=False)
    mem_id = db.Column(db.Integer, nullable=False)
    mem_name = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    contribution = db.Column(db.Float, default=0.0)

# | Notification database model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    recv = db.Column(db.Integer, nullable=False)
    attachment = db.Column(db.String)
    badge = db.Column(db.String) # [team, user, app]

# | Uesr settings database model
class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    
    # * Appearance
    theme = db.Column(db.String, default='light') # [light, dark]
    accent = db.Column(db.String, default='blue') # [blue, green, red, yellow]
    chart_color_schemes = db.Column(db.String, default='classic') # [classic, modern]
    chart_type = db.Column(db.String, default='doughnut') # [doughnut, bar]

    # * Profile
    skills = db.Column(db.JSON, default=lambda: ["No skill"] * 5)
    from_hours = db.Column(db.Time, default=time(9, 0))
    to_hours = db.Column(db.Time, default=time(17, 0))
    
    # * Security
    passkey = db.Column(db.String) # 6 digit code
    password = db.Column(db.String)
    password_rotation = db.Column(db.Boolean, default=False)

    # * Advanced
    pre_release = db.Column(db.Boolean, default=False)

# | Social link database model
class SocialLink(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    link = db.Column(db.String)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "url": self.link
        }
    
# | Subscription database model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)

# | Skills database model
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String, nullable=False)
    skill = db.Column(db.String, nullable=False)

# | Join request database model
class JoinReq(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    req = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    team_id = db.Column(db.Integer, nullable=False)

# ! Initializing default variables
CMD: list = ['@', '.', '!', '$']
CURRENT_VERSION = 'v0.9.0'

# & function to refresh contribution
def refresh_contribution(project: Project):
        if not project.team_id:
            return
        
        all_objectives = len(Objective.query.filter_by(project_id=project.id).all())
        
        for member in Member.query.filter_by(team_id=project.team_id):
            done_objectives = len(Objective.query.filter_by(
                project_id=project.id,
                isdone=True,
                doneby=member.id
            ).all())

            contribution = round((done_objectives / all_objectives) * 100, 1) if (done_objectives > 0) else 0
            member.contribution = contribution
            db.session.commit()