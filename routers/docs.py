'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash
from extensions import *

# ! Buliding docs router
docs = Blueprint('docs', __name__, url_prefix='/docs')

# | Context Processor
@docs.context_processor
def inject_common_vars():
    try:
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        return {'settings': settings}
    
    except:
        return {
            'settings': {
                'theme': 'light',
                'accent': 'blue',
                'chart_color_shcemes': 'modern'
            }
        }
    

# & Home route
@docs.route('/')
def home():
    return render_template('docs/home.html')

# & Overivew page route
@docs.route('/overview/')
def docs_overview():
    return render_template('docs/overview.html')

# & Profile page route
@docs.route('/profile/')
def docs_profile():
    return render_template('docs/profile.html')

# & Teams page route
@docs.route('/teams')
def docs_teams():
    return render_template('docs/teams.html')

# & Project page route
@docs.route('/projects')
def docs_project():
    return render_template('docs/project.html')

# & Command-pallet page route
@docs.route('/command-pallet')
def docs_cmd():
    return render_template('docs/cmd.html')
