'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from datetime import date, datetime
from extensions import *

# ! Building project router
project = Blueprint('project', __name__, url_prefix='/projects')

# * socket route to mark objectives
@socket.on('mark-obj')
def mark_objective(data):
    obj = Objective.query.filter_by(id=data['obj_id']).first()
    project = Project.query.filter_by(id=data['route']).first()
    team = Team.query.filter_by(id=data['team_id']).first()
    total_objectives = Objective.query.filter_by(project_id=project.id).all()

    if not team:
        obj.isdone = True
        db.session.commit()
        socket.emit('mark-obj-callback', {
            'status': 200,
        })
        return

    member = Member.query.filter_by(
        mem_id=data['user_id'],
        team_id=team.id
    ).first()

    obj.isdone = True
    obj.doneby = member.id
    db.session.commit()

    done_objectives = Objective.query.filter_by(
        project_id=project.id,
        doneby=member.id
    ).all()

    member.contribution = round(
        len(done_objectives) / len(total_objectives) * 100,
        1
    )
    db.session.commit()

    socket.emit('mark-obj-callback', {
        'status': 200,
    })

# * socket route to delete objectives
@socket.on('delete-obj')
def delete_objectives(data):
    obj = Objective.query.filter_by(id=data['obj_id']).first()
    db.session.delete(obj)
    db.session.commit()

    socket.emit('del-obj-callback', {
        'status': 200,
    })

# * socket route to update project visibility
@socket.on('project-settings')
def update_project_visibility(data):
    try:
        project = Project.query.filter_by(id=data['projectId']).first()

        if not project:
            socket.emit('project-settings-callback', {'status': 404})

        project.private = data['private']
        db.session.commit()
        socket.emit('project-settings-callback', {'status': 200})

    except:
        socket.emit('project-settings-callback', {'status': 500})

# | Context Processor
@project.context_processor
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

# & Project route
@project.route('/<int:id>/')
@login_required
def show_project(id):
    project = Project.query.filter_by(id=id).first()
    refresh_contribution(project)

    if project.team_id:
        team = Team.query.filter_by(id=project.team_id).first()

        if (not Member.query.filter_by(
            mem_id=current_user.id,
            team_id=team.id
        ).first()) and (project.private):
            flash("You can't see this project as it's private.", "error")
            return redirect(url_for('router.dashboard'))
        
        if (Member.query.filter_by(
            mem_id=current_user.id,
            team_id=team.id
        ).first()):
            access = True

        else: access = False

        viewer = Member.query.filter_by(
            admin=True,
            team_id=team.id
        ).first()

    else:
        viewer = User.query.filter_by(id=project.created_by).first()
        
        if (not current_user.id == viewer.id) and (project.private):
            flash("You can't see this project as it's private.", "error")
            return redirect(url_for('router.dashboard'))

        team = None
        access = True if (current_user.id == viewer.id) else False
        
    try: viewerid = viewer.id
    except: viewerid = 0
    isadmin = True if current_user.id == viewer.id else False

    objectives = Objective.query.filter_by(project_id=project.id).all()
    completed_obj = len(
        Objective.query.filter_by(
            project_id=project.id,
            isdone=True
        ).all()
    )
    incomplete_obj = len(
        Objective.query.filter_by(
            project_id=project.id,
            isdone=False
        ).all()
    )

    return render_template('pages/project.html', data={
        'project': project,
        'team': team,
        'objectives': objectives,
        'objectives_overview': {
            'completed': completed_obj if completed_obj > 0 else 0,
            'incomplete': incomplete_obj if incomplete_obj > 0 else 0
        },
        'viewer': {
            'id': viewerid,
            'is_admin': isadmin,
        },
        'access': access
    })

# & Project settings route
@project.route('/<int:id>/settings/')
def project_settings(id):
    project = Project.query.filter_by(id=id).first()

    if (not current_user.id == project.created_by):
        abort(404)

    memberships = Member.query.filter_by(mem_id=current_user.id).all()
    selected_team = None

    teams = [
        Team.query.filter_by(id=membership.team_id).first() 
        for membership in memberships
    ]
    teams_ids = [team.id for team in teams]

    if project.team_id:
        selected_team = Team.query.filter_by(id=project.team_id).first()
        teams_ids.remove(selected_team.id)

    teams = [
        Team.query.filter_by(id=team_id).first() 
        for team_id in teams_ids
    ]

    return render_template('pages/project-settings.html', data={
        'project': project,
        'teams': teams,
        'selected_team': selected_team
    })

# & Update project settings route
@project.route('/<int:id>/settings/update/<category>', methods=['POST'])
def update_project_settings(id, category):
    project = Project.query.filter_by(id=id).first()

    if category == 'basic':
        project.title = request.form.get('title')
        project.desc = request.form.get('desc', "")

    if category == 'team':
        project.team_id = int(request.form.get('current_team', 0))

    db.session.commit()
    flash("Project settings has been updated.", 'success')
    return redirect(url_for('project.project_settings', id=id))

# & New project route
@project.route('/new', methods=['POST'])
@login_required
def add_new_project():
    title = request.form.get('title', 'Untitled project')
    desc = request.form.get('desc', "")
    team = request.form.get('team')
    st = datetime.strptime(request.form.get('st'), "%Y-%m-%d").date()
    en = datetime.strptime(request.form.get('en'), "%Y-%m-%d").date()

    team = int(team) if team else None

    new_project = Project(
        created_by=current_user.id,
        title=title,
        desc=desc,
        team_id=team,
        start_date=st,
        end_date=en,
    )

    db.session.add(new_project)
    db.session.commit()
    flash("New project has been created.", "success")
    return redirect(url_for('project.show_project', id=new_project.id))

# & Delete project route
@project.route('/delete')
@login_required
def delete_project():
    project_id = int(request.args.get('project-id', 0))
    
    try:
        # Delete project objectives
        for objective in Objective.query.filter_by(project_id=project_id).all():
            db.session.delete(objective)
            db.session.commit()

        # Delete project data
        project = Project.query.filter_by(id=project_id).first()
        db.session.delete(project)
        db.session.commit()
        
        flash("The project has been deleted.", "success")
        return redirect(url_for('router.dashboard'))
    
    except:
        flash("Something went wrong.", "error")
        return redirect(url_for('router.dashboard'))

# & New objective route
@project.route('/<int:id>/objectives/new', methods=['POST'])
@login_required
def new_objective(id):
    current_project = Project.query.filter_by(id=id).first()
    obj = request.form.get('obj')

    new_obj = Objective(
        task=obj,
        project_id=current_project.id
    )

    db.session.add(new_obj)
    db.session.commit()

    flash("New objective added successfully.", "success")
    return redirect(url_for('project.show_project', id=id))