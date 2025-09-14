'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import date, datetime
import json
from extensions import *

# ! Building main router
router = Blueprint('router', __name__)

# | LOGGER route
@logger.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# * socket route for 'notification-seen'
@socket.on('notification-seen')
def handle_notification_seen(id):
    notification = Notification.query.get(id)
    if notification:
        db.session.delete(notification)
        db.session.commit()

# * socket route for 'update-settings'
@socket.on('update-settings')
def update_settings(data: dict):
    # | Get settings db row
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        socket.emit('update-settings-callback', {'status': 404, 'message': 'Settings not found'})
        return

    try:
        # | Update appearance settings
        appearance: dict = data.get('appearance', {})
        settings.theme = appearance.get('theme', settings.theme)
        settings.accent = appearance.get('accent', settings.accent)
        settings.chart_color_schemes = appearance.get('chartColor', settings.chart_color_schemes)
        settings.chart_type = appearance.get('chartType', settings.chart_type)

        # | Update profile settings
        profile: dict = data.get('profile', {})
        settings.skills = profile.get('skills', settings.skills)
        settings.from_hours = datetime.strptime(profile.get('workingHours').get('from', "09:00"), "%H:%M").time()
        settings.to_hours = datetime.strptime(profile.get('workingHours').get('to', "17:00"), "%H:%M").time()

        # | Update social links
        for sociallink in SocialLink.query.filter_by(user_id=current_user.id).all():
            db.session.delete(sociallink)
            db.session.commit()

        for link in profile.get('socialLinks', {}):
            new_link = SocialLink(
                user_id=current_user.id,
                title=link.get('title', ''),
                link=link.get('url', '')
            )
            db.session.add(new_link)
            db.session.commit()

        # | Update security settings
        security: dict = data.get('security', {})
        settings.password_rotation = security.get('passwordRotation', settings.password_rotation)

        # | Update advanced setings
        advanced: dict = data.get('advanced', {})
        version: dict = advanced.get('version')
        settings.pre_release = version.get('isPreRelease', settings.pre_release)

        db.session.commit()
        socket.emit('update-settings-callback', {'status': 200, 'message': 'Settings saved successfully.'})

    except Exception as e:
        socket.emit('update-settings-callback', {'status': 500, 'message': e})

# | Context Processor
@router.context_processor
def inject_common_vars():
    projects = Project.query.filter_by(created_by=current_user.id).all()
    notifications = Notification.query.filter_by(recv=current_user.id).all()
    all_teams = Team.query.all()
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    active_projects = []
    completed_projects = []
    pending_projects = []
    failed_projects = []
    teams = []
    today = date.today()

    if all_teams:
        for team in all_teams:
            for mem in Member.query.filter_by(team_id=team.id).all():
                if mem.mem_id == current_user.id:
                    teams.append(team)
                    break

    if len(projects) < 1:
        return {
            'active_projects': 0,
            'completed_projects': 0,
            'pending_projects': 0,
            'failed_projects': 0,
            'total_projects': 0,
            'allteams': teams,
            'notification_count': len(notifications),
            'notifications': notifications,
            'settings': settings,
            'CURRENT_VERSION': CURRENT_VERSION,
        }
    

    for project in projects:
        if project.done:
            completed_projects.append(project)
        elif project.start_date > today:
            pending_projects.append(project)
        elif project.end_date < today and not project.done:
            failed_projects.append(project)
        elif project.start_date <= today <= project.end_date and not project.done:
            active_projects.append(project)

    return {
        'active_projects': len(active_projects),
        'completed_projects': len(completed_projects),
        'pending_projects': len(pending_projects),
        'failed_projects': len(failed_projects),
        'total_projects': len(projects),
        'allteams': teams,
        'notification_count': len(notifications),
        'notifications': notifications,
        'settings': settings,
        'CURRENT_VERSION': CURRENT_VERSION,
    }

# & Base route
@router.route('/')
def index():
    if current_user.is_authenticated: 
        return redirect(url_for('router.dashboard'))
    else:
        return redirect(url_for('auth.signup'))
    
# & Dashboard route
@router.route('/dashboard/')
@login_required
def dashboard():
    projects = Project.query.filter_by(created_by=current_user.id).all()

    return render_template('pages/dash.html', data={
        'projects': projects,
        'today': date.today()
    })

# & Profile route
@router.route('/profile/')
@login_required
def show_profile():
    userid = int(request.args.get('userid', current_user.id))
    user = User.query.filter_by(id=int(userid)).first_or_404("User not found.")
    sociallinks = SocialLink.query.filter_by(user_id=userid).all()[:3]
    usersettings = UserSettings.query.filter_by(user_id=userid).first()

    # filter sociallink
    sociallinks = [link for link in sociallinks if link.link]

    projects = Project.query.filter_by(created_by=userid).all()
    active_projects = []
    completed_projects = []
    pending_projects = []
    failed_projects = []
    today = date.today()

    if len(projects) < 1:
        return render_template('pages/profile.html', data={
            'user': user,
            'sociallinks': sociallinks,
            'skills': usersettings.skills,
            'projects': {
                'active': 0,
                'completed': 0,
                'pending': 0,
                'failed': 0,
                'total': 0,
            }
        })
    
    for project in projects:
        if project.done:
            completed_projects.append(project)
        elif project.start_date > today:
            pending_projects.append(project)
        elif project.end_date < today and not project.done:
            failed_projects.append(project)
        elif project.start_date <= today <= project.end_date and not project.done:
            active_projects.append(project)

    return render_template('pages/profile.html', data={
        'user': user,
        'sociallinks': sociallinks,
        'skills': usersettings.skills,
        'projects': {
            'active': len(active_projects),
            'completed': len(completed_projects),
            'pending': len(pending_projects),
            'failed': len(failed_projects),
            'total': len(projects),
        }
    })

# | Update profile route
@router.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    UPLOADS = os.path.join(current_app.root_path, "static", "public")
    name = request.form.get('name', current_user.name)
    email = request.form.get('email', current_user.email)
    bio = request.form.get('bio')
    pic = request.files.get('pic')
    mems = Member.query.filter_by(mem_name=current_user.name).all()

    if pic:
        ext = ".png"

        filename = f"{current_user.id}{ext}"
        save_path = os.path.join(UPLOADS, filename)
        print("Saving to:", save_path)
        pic.save(save_path)
        current_user.pic = f"/static/public/{filename}"

    current_user.name = name
    current_user.email = email
    current_user.bio = bio
    db.session.commit()

    for mem in mems:
        mem.mem_name = current_user.name
        db.session.commit()

    flash("Your profile has been updated.", "success")
    return redirect(url_for('router.show_profile'))

# & Search user route
@router.route('/users/')
@login_required
def search_user():
    userid = request.args.get('userid')
    skill = request.args.get('skill')

    if skill:
        skill = skill[1:]
        all_settings = UserSettings.query.all()
        users_with_skills = [user for user in all_settings if skill in user.skills]
        users = [User.query.get(user.user_id) for user in users_with_skills]

    elif userid: users = User.query.filter(User.name.ilike(f'%{userid}%')).all()
    else: users = User.query.all()

    return render_template('pages/users.html', data={
        'users': users,
    })

# & Settings page route
@router.route('/settings/')
@login_required
def settings():
    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    social_links = SocialLink.query.filter_by(user_id=current_user.id).all()

    return render_template('pages/settings.html', data={
        'user_settings': user_settings,
        'social_links': social_links
    })

# & Search route
@router.route('/search/')
def search_query():
    query = request.args.get('query')

    # Get users by name
    users_by_name = User.query.filter(
        User.name.ilike(f'%{query}%')
    ).all()

    # Get users by email
    users_by_email = User.query.filter(
        User.email.ilike(f'%{query}%')
    ).all()

    # Get skills
    skills = Skill.query.filter(
        Skill.skill.ilike(f'%{query}%') |
        Skill.category.ilike(f'%{query}%')
    ).all()

    # Get teams
    teams = Team.query.filter(
        Team.title.ilike(f'%{query}%'),
        Team.private == False
    ).all()

    # Get projects
    projects = Project.query.filter(
        Project.title.ilike(f'%{query}%'),
        Project.private == False
    ).all()

    return render_template('pages/search.html', data={
        'query': query,
        'users_by_name': users_by_name,
        'users_by_email': users_by_email,
        'skills': skills,
        'teams': teams,
        'projects': projects
    })