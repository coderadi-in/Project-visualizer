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
    flash("Docs will be availiable from version 1.0.0", "warning")
    return redirect(url_for('router.dashboard'))