'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import *

# ! Building auth router
auth = Blueprint('auth', __name__, url_prefix='/auth')

# & Signup route
@auth.route('/signup/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated: return redirect(url_for('router.dashboard'))
    if request.method == 'GET': return render_template('auth/signup.html')

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash("User already exists. Try signing up instead.", "warning")
        return redirect(url_for('auth.signup'))

    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    user_settings = UserSettings(user_id=new_user.id)
    db.session.add(user_settings)
    db.session.commit()

    for _ in range(3):
        db.session.add(SocialLink(user_id=new_user.id))
        db.session.commit()

    login_user(new_user)
    flash("You're signed up successfully.", "success")
    return redirect(url_for('router.dashboard'))

# & Login route
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('router.dashboard'))
    if request.method == 'GET': return render_template('auth/login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found. Try signing up instead.", "error")
        return redirect(url_for('auth.login'))
    
    if not hashout(user.password, password):
        flash("Invalid password.", "error")
        return redirect(url_for('auth.login'))
    
    login_user(user)
    flash("You're logged in.", 'success')
    return redirect(url_for('router.dashboard'))
    
# & GOOGLE login route
@auth.route('/login/google/')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('router.dashboard'))
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

# & GOOGLE login callback route
@auth.route('/login/google/callback')
def google_authorize():
    try:
        token = oauth.google.authorize_access_token()
        
        user_info = token.get('userinfo')
        if not user_info:
            user_info = oauth.google.get('userinfo').json()
        
        if not user_info.get('email'):
            flash('Google login failed: No email provided', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(
                googleid=user_info.get('sub'),
                name=user_info.get('name', 'User'),
                email=user_info['email'],
                pic=user_info['picture']
            )
            db.session.add(user)
            db.session.commit()

            user_settings = UserSettings(user_id=user.id)
            db.session.add(user_settings)
            db.session.commit()

            for _ in range(3):
                db.session.add(SocialLink(user_id=user.id))
                db.session.commit()
        else:
            if not user.googleid:
                user.googleid = user_info.get('sub')
        
        db.session.commit()
        login_user(user)
        flash('Logged in successfully with Google.', 'success')
        return redirect(url_for('router.dashboard'))
        
    except Exception as e:
        flash('Failed to log in with Google. Please try again.', 'error')
        return redirect(url_for('auth.signup'))
    
# & Logout route
@auth.route('/logout/')
def logout():
    if not current_user.is_authenticated: return redirect(url_for('auth.login'))
    logout_user()
    flash("You're logged out.", "success")
    return redirect(url_for('auth.login'))

# & Delete account route
@auth.route('/delete')
def delete_account():
    user = User.query.filter_by(id=current_user.id).first()
    projects = Project.query.filter_by(created_by=current_user.id).all()

    objectives = []
    for project in projects:
        objective = Objective.query.filter_by(project_id=project.id).all()
        for obj in objective:
            objectives.append(obj)

    members = Member.query.filter_by(mem_id=current_user.id).all()
    notifications = Notification.query.filter_by(recv=current_user.id).all()
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    social_links = SocialLink.query.filter_by(user_id=current_user.id).all()

    db.session.delete(user)
    db.session.delete(settings)
    db.session.commit()

    for objective in objectives:
        db.session.delete(objective)
        db.session.commit()

    for project in projects:
        db.session.delete(project)
        db.session.commit()

    for member in members:
        db.session.delete(member)
        db.session.commit()

    for notification in notifications:
        db.session.delete(notification)
        db.session.commit()

    for link in social_links:
        db.session.delete(link)
        db.session.commit()

    flash("Your account is now deleted permanently.", "warning")
    return redirect(url_for('auth.signup'))