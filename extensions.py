'''coderadi'''

# ? Importing libraries
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate, init, stamp, migrate, upgrade
from flask_apscheduler import APScheduler
from flask_mail import Mail, Message
from sqlalchemy import func, inspect, text, or_

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
from datetime import time, date
import datetime
import os
import secrets

# ! Building extensions
db = SQLAlchemy()
logger = LoginManager()
migrator = Migrate(directory='updates')
socket = SocketIO()
oauth = OAuth()
mail = Mail()
worker = APScheduler()

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
    migrator.init_app(server, db)
    socket.init_app(server)
    oauth.init_app(server)
    mail.init_app(server)
    worker.init_app(server)

# | User database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    googleid = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    bio = db.Column(db.Text(100), default="")
    pic = db.Column(db.String, default='/static/assets/icons/common/profile.png')
    passkey = db.Column(db.String) # 6 digit code
    password = db.Column(db.String)

# | Project database model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, default="Untitled project")
    desc = db.Column(db.String(100))
    private = db.Column(db.Boolean, default=False)
    status = db.Column(db.String) # [active, not-started, failed, completed]
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

# | Feedback database model
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    feed = db.Column(db.Text, nullable=False)

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

# | Hosting database model
class Hosting(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    charge = db.Column(db.Integer, nullable=False)

# ! Initializing default variables
CMD: list = ['@', '.', '!', '$']
CURRENT_VERSION = 'v1.0.0'
HOSTING_CHARGE = 768
SKILLS_FILE = 'skills.json' # ! Skills file path
QTY = 0
FOLDERS = [
    'static/public'
]

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

# & function to add basic details of the app
def add_basic_details():
    # * check hosting
    if not Hosting.query.first():
        print("Adding hosting details...")
        hosting = Hosting(
            start_date=date.today(),
            end_date=date.today() + datetime.timedelta(days=30),
            charge=768
        )
        db.session.add(hosting)
        db.session.commit()
        print("Added hosting details.")

# & migration function
def migrate_db(message="auto migration"):
    """
    Migrates the database with added new tables/columns

    ## Parameters
    ## `message`
    - Labels the migration script.
    - Default: `auto migration`
    """

    with current_app.app_context():
        if (not os.path.exists('updates')):
            init()
            stamp()

        # ? Migration the database update
        migrate(message=message)
        upgrade()

# & Function to update project status
def update_project_status(project: Project):
    today = date.today()
    project_objectives = Objective.query.filter_by(project_id=project.id).count()
    done_objectives = Objective.query.filter_by(project_id=project.id, isdone=True).count()
    project.status = 'pending'

    if (project_objectives == 0) or (project.start_date > today):
        project.status = 'pending'
        db.session.commit()
        return
    
    if (project_objectives != 0):
        timeline = project.start_date <= today <= project.end_date
        if (project_objectives == done_objectives) and (timeline):
            project.status = 'completed'

        elif (done_objectives < project_objectives) and (timeline):
            project.status = 'active'

        elif (done_objectives < project_objectives) and (not timeline):
            project.status = 'failed'

    db.session.commit()
        
# & Function to generate random passwords
def set_random_pass(user_id: int):
    psw = secrets.token_urlsafe(10)
    user = User.query.get(user_id)
    user.password = hashin(psw)
    db.session.commit()
    print(psw)

    notification = Notification(
        title="New password",
        message=f"Your new app password is {psw}",
        recv=user_id,
        badge="app"
    )

    db.session.add(notification)
    db.session.commit()