'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import *

# ! Building server
app = Blueprint('app', __name__, url_prefix='/app')

# | Context processor
@app.context_processor
def inject_common_vars():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()

    return {
        "settings": {
            "theme": user_settings.theme,
            "accent": user_settings.accent
        }
    }

# & Subscription route
@app.route('/subscription', methods=['POST'])
@login_required
def subscribe():
    email = request.form.get('email')
    subscription = Subscription.query.filter_by(email=email).first()
        
    if subscription:
        flash("You've already subscribed our newsletter.", "warning")
        return redirect(url_for('docs.home'))

    new_subscription = Subscription(email=email)
    db.session.add(new_subscription)
    db.session.commit()
    flash("You've now subscribed our newsletter.", "success")
    return redirect(url_for('docs.home'))

# & Feedback route
@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    email = request.form.get('email')
    feed = request.form.get('feedback')

    new_feed = Feed(
        email=email,
        feed=feed
    )
    db.session.add(new_feed)
    db.session.commit()
        
    flash("Thanks for the feedback.", "success")
    return redirect(url_for('docs.home'))

# & Announcements page
@app.route('/announcements/')
@login_required
def announcements():
    version = request.args.get('version')

    if not version:
        return render_template('updates/home.html')
        
    try:
        return render_template(f'updates/{version}.html')
    except:
        print(">>>> Flashing...")
        flash(f"We haven't completed the documentation yet for version {version}.", "error")
        return render_template('updates/home.html')