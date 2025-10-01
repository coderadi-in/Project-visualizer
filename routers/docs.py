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

# & Projects route
@docs.route('/projects')
def projects():
    return render_template('docs/projects.html')

# & Teams route
@docs.route('/teams')
def teams():
    return render_template('docs/teams.html')

# & Profile route
@docs.route('/profile')
def profile():
    return render_template('docs/profile.html')

# & Updates route
@docs.route('/updates')
def updates():
    return render_template('docs/updates.html')