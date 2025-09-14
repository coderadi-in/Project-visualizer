'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from sqlalchemy.sql.dml import ReturningUpdate
from extensions import *
from datetime import date

# ! Building team router
team = Blueprint('team', __name__, url_prefix="/teams")

# * function to check if the team exists
def check_team(team_id: int):
    if not Team.query.filter_by(id=team_id).first():
        flash("Something went wrong! Try reloading the page.", "error")
        return redirect(url_for('team.index'))
    
# * Socket route for team-visibility
@socket.on('team-settings')
def toggle_visibility(data):
    team = Team.query.filter_by(id=data['teamId']).first()
    team.private = data['private']
    db.session.commit()

    socket.emit('team-settings-callback', {
        'status': 200
    })

    user = User.query.filter_by(id=data['memId']).first()

    notification = Notification(
        title="Team demotion",
        message="You're now demoted to member of the team.",
        recv=user.id,
        attachment=f"/teams/{data['teamId']}",
        badge="team"
    )

    db.session.add(notification)
    db.session.commit()

# * socket route to add-moderator
@socket.on('add-moderator')
def add_moderator(data):
    member = Member.query.filter_by(
        team_id=data['teamId'],
        mem_id=data['memId']
    ).first()

    if not member:
        socket.emit('add-moderator-callback', {'status': 404})
        return

    member.admin = True
    db.session.commit()
    socket.emit('add-moderator-callback', {'status': 200})
    user = User.query.filter_by(id=data['memId']).first()

    notification = Notification(
        title="Team promotion",
        message="You're now promoted to moderator of the team.",
        recv=user.id,
        attachment=f"/teams/{data['teamId']}",
        badge="team"
    )

    db.session.add(notification)
    db.session.commit()

# * socket route to remove-moderator
@socket.on('remove-moderator')
def remove_moderator(data):
    member = Member.query.filter_by(
        team_id=data['teamId'],
        mem_id=data['memId']
    ).first()

    if not member:
        socket.emit('add-moderator-callback', {'status': 404})
        return
    
    member.admin = False
    db.session.commit()
    socket.emit('remove-moderator-callback', {'status': 200})
    user = User.query.filter_by(id=data['memId']).first()

    notification = Notification(
        title="Team demotion",
        message="You're demoted to member of the team.",
        recv=user.id,
        attachment=f"/teams/{data['teamId']}",
        badge="team"
    )

    db.session.add(notification)
    db.session.commit()

# * socket route to remove member
@socket.on('remove-member')
def remove_member(data):
    member = Member.query.filter_by(
        mem_id=data['memId'],
        team_id=data['teamId']
    ).first()

    print(data['memId'], data['teamId'])
    print(member, member.mem_id)

    if not member:
        socket.emit('add-moderator-callback', {'status': 404})
        return

    db.session.delete(member)
    db.session.commit()
    socket.emit('remove-member-callback', {'status': 200})
    user = User.query.filter_by(id=data['memId']).first()

    notification = Notification(
        title="Team separation",
        message="You're removed from the team.",
        recv=user.id,
        attachment=f"/teams/{data['teamId']}",
        badge="team"
    )

    db.session.add(notification)
    db.session.commit()

# | Context Processor
@team.context_processor
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
    }

# & New team route
@team.route('/new', methods=['POST'])
@login_required
def new_team():
    title = request.form.get('title')

    new_team = Team(title=title)
    db.session.add(new_team)
    db.session.commit()

    main_member = Member(
        mem_id=current_user.id,
        mem_name=current_user.name,
        team_id=new_team.id,
        admin=True
    )
    
    db.session.add(main_member)
    db.session.commit()

    flash("New team has been added.", "success")
    return redirect(url_for('team.index'))

# & Team index route
@team.route('/')
@login_required
def index():
    team_title = request.args.get('title')
    role = request.args.get('role')

    if (role) and (not team_title):
        if (role == 'member'):
            team_ids = [mem.team_id for mem in Member.query.filter_by(mem_id=current_user.id).all()]
            all_teams = [Team.query.filter_by(id=team_id).first() for team_id in team_ids]

        elif (role == 'moderator'):
            team_ids = [mem.team_id for mem in Member.query.filter_by(
                mem_id=current_user.id,
                admin=True
            ).all()]
            all_teams = [Team.query.filter_by(id=team_id).first() for team_id in team_ids]

        else: all_teams = Team.query.all()

    elif team_title:
        all_teams = Team.query.filter(
            Team.title.ilike(f'%{team_title}%')
        ).all()

    else: all_teams = Team.query.all()
    
    teams = [{
        'data': team,
        'projects': {
            'completed': 0,
            'active': 0,
            'pending': 0,
            'failed': 0,
        }
    } for team in all_teams if (not team.private)]
    today = date.today()

    for team in teams:
        for project in Project.query.filter_by(team_id=team['data'].id).all():
            if project.done:
                team['projects']['completed'] += 1
            elif project.start_date > today:
                team['projects']['pending'] += 1
            elif project.end_date < today and not project.done:
                team['projects']['failed'] += 1
            elif project.start_date <= today <= project.end_date and not project.done:
                team['projects']['active'] += 1

    return render_template('pages/team.html', data={
        'teams': teams
    })

# & Specific team route
@team.route('/<int:id>')
@login_required
def team_page(id):
    team = Team.query.filter_by(id=id).first()
    projects = Project.query.filter_by(team_id=id).all()
    members = Member.query.filter_by(team_id=id).all()
    today = date.today()

    check_team(id) # ! Check if the team exists

    current_member = Member.query.filter_by(
        mem_id=current_user.id,
        team_id=team.id
    ).first()

    if (not current_member) and (team.private):
        flash("You can't view this team as it's private.", "warning")
        return redirect(url_for('router.dashboard'))

    # Viewer's accessibilitly
    viewer = {
        'is_admin': current_member.admin if current_member else False,
        'is_member': True if current_member else False
    }

    return render_template('pages/team-page.html', data={
        'team': team,
        'projects': projects,
        'members': members,
        'viewer': viewer,
        'today': today,
    })

# & New memeber route
@team.route('/<int:id>/members/new', methods=['POST'])
@login_required
def new_member(id):
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    team = Team.query.filter_by(id=id).first()

    check_team(id) # ! Check if the team exists

    if not user:
        flash("User with given email not found.", "error")
        flash("Check if the email is correct.", "error")
        return redirect(url_for('team.team_page', id=id))
    
    if Member.query.filter_by(team_id=id, mem_id=user.id).first():
        flash("User is already a member of this team.", "error")
        return redirect(url_for('team.team_page', id=id))
    
    new_mem = Member(
        mem_id=user.id,
        mem_name=user.name,
        team_id=id,
    )

    db.session.add(new_mem)
    db.session.commit()

    team.members += 1
    db.session.commit()

    new_notification = Notification(
        title="New team joining.",
        message="You've been joined in a new team",
        attachment=f"/teams/{id}",
        recv=user.id,
        badge="team",
    )

    db.session.add(new_notification)
    db.session.commit()

    flash("New member has been added.", "success")
    return redirect(url_for('team.team_page', id=id))

# & Delete member route
@team.route('<int:id>/members/delete')
@login_required
def delete_member(id):
    member = Member.query.filter_by(id=request.args.get('mem-id')).first()
    check_team(id) # ! Check if the team exists

    if not member:
        flash("Something went wrong.", "error")
        return redirect(url_for('team.team_page', id=id))
    
    db.session.delete(member)
    db.session.commit()

    flash("The member has been deleted.", "success")
    return redirect(url_for('team.team_page', id=id))

# & Team settings page route
@team.route('/<int:id>/settings/')
@login_required
def settings_page(id):
    team = Team.query.filter_by(id=id).first()
    check_team(id) # ! Check if the team exists
    members = Member.query.filter_by(team_id=team.id).all()

    if not Member.query.filter_by(
        mem_id=current_user.id,
        team_id=team.id,
        admin=True
    ).first():
        abort(404)

    joinreqs = JoinReq.query.filter_by(team_id=team.id).all()
    
    return render_template('pages/team-settings.html', data={
        'team': team,
        'members': members,
        'joinreqs': joinreqs
    })

# | Update settings route
@team.route('/<int:id>/settings/update', methods=['POST'])
@login_required
def update_team_settings(id):
    team = Team.query.filter_by(id=id).first()
    check_team(id)

    UPLOADS = os.path.join(current_app.root_path, "static", "public")
    title = request.form.get('title', team.title)
    desc = request.form.get('desc', '')
    icon = request.files.get('icon')

    team.title = title
    team.desc = desc

    if icon:
        ext = ".png"

        filename = f"team-{team.id}{ext}"
        savepath = os.path.join(UPLOADS, filename)
        icon.save(savepath)
        team.icon = f"/static/public/{filename}"

    db.session.commit()
    flash("Team settings has been updated.", "success")
    return redirect(url_for('team.settings_page', id=id))

# & New join request route
@team.route('/<int:id>/reqs/new')
def new_req(id):
    team = Team.query.filter_by(id=id).first()
    check_team(id) # ! Check if team exists

    team_moderators = Member.query.filter_by(
        team_id=team.id,
        admin=True
    ).all()

    if JoinReq.query.filter_by(
        req=current_user.id,
        team_id=team.id,
    ).first():
        flash("You're already requests this team", "error")
        return redirect(url_for('team.team_page', id=id))

    new_join_req = JoinReq(
        name=current_user.name,
        req=current_user.id,
        team_id=team.id,
    )    

    db.session.add(new_join_req)
    db.session.commit()

    for moderator in team_moderators:
        notification = Notification(
            title="New join request",
            message="A user wants to join your team.",
            recv=moderator.id,
            attachment=f"/teams/{team.id}/settings/#join-reqs",
            badge='team',
        )

        db.session.add(notification)
        db.session.commit()

    flash("You request is sent.", "success")
    return redirect(url_for('team.team_page', id=id))

# & Add member route
@team.route('/<int:id>/reqs/accept')
def accent_req(id):
    team = Team.query.filter_by(id=id).first()
    check_team(id) # ! Check if team exists

    req_id = request.args.get('req-id', 0)
    req = JoinReq.query.filter_by(id=req_id).first()
    user = User.query.filter_by(id=req.req).first()

    if user:
        new_mem = Member(
            team_id=team.id,
            mem_id=user.id,
            mem_name=user.name,
        )
        db.session.add(new_mem)
        db.session.commit()

        notify = Notification(
            title="New team joining.",
            message="You've been joined into a new team.",
            recv=user.id,
            attachment=f'/teams/{team.id}',
            badge='team'
        )
        db.session.add(notify)
        db.session.commit()

    db.session.delete(req)
    db.session.commit()
    return redirect(url_for('team.settings_page', id=id))

# & Deny request route
@team.route('/<int:id>/reqs/deny')
def deny_req(id):
    team = Team.query.filter_by(id=id).first()
    check_team(id) # ! Check if team exists

    req_id = request.args.get('req-id', 0)
    req = JoinReq.query.filter_by(id=req_id).first()
    user = User.query.filter_by(id=req.req).first()

    if user:
        notify = Notification(
            title="Requests denied.",
            message="Your request to jion the team was not accenpt.",
            recv=user.id,
            attachment=f'/teams/{team.id}',
            badge='team'
        )
        db.session.add(notify)
        db.session.commit()

    db.session.delete(req)
    db.session.commit()
    return redirect(url_for('team.settings_page', id=id))