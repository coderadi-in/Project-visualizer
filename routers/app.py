'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import *

# ! Building server
app = Blueprint('app', __name__, url_prefix='/app')

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

    content = f"""Hi Adi!
Someone has given you feedback on your app - "Project Visualizer".
Email:
{email if email else "Empty"}
---
Feed:
{feed}"""
    
    print(content)
    flash("Thanks for the feedback.", "success")
    return redirect(url_for('docs.home'))