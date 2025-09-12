'''coderadi'''

# ? Importing libraries
from flask import Blueprint, request, jsonify
from extensions import *
import json
from datetime import datetime, date

today = date.today()

# ! Building api router
api = Blueprint('api', __name__, url_prefix='/api')

# & Route to get all projects overview
@api.route('/dashboard/projects')
def get_projects_overview():
    user = int(request.args.get('userid'))
    projects = Project.query.filter_by(
        created_by=user
    ).all()

    completed = Project.query.filter_by(
        created_by=user,
        done=True
    ).count()

    active = [
        project for project in projects
        if not project.done
        and project.start_date <= today
        and project.end_date >= today
    ]

    pending = [
        project for project in projects
        if not project.done
        and project.start_date > today
    ]

    return jsonify({
        'completed': completed,
        'active': len(active),
        'pending': len(pending)
    })

# & Route to get left time to complete project
@api.route('/project/<int:id>/time-data')
def get_time_data(id):
    user = int(request.args.get('userid'))
    team_id = request.args.get('teamid', 0)
    team_id = int(team_id) if team_id else None

    if team_id:
        project = Project.query.filter_by(
            id=id,
            team_id=team_id
        ).first()
    else:
        project = Project.query.filter_by(
            created_by=user,
            id=id
        ).first()

    total_time = int((project.end_date - project.start_date).days)
    left_time = int((project.end_date - today).days)

    return jsonify({
        'spent_time': total_time-left_time,
        'left_time': left_time
    })

# & Route to get tasks overview
@api.route('/project/<int:id>/task-data')
def get_task_data(id):
    user = int(request.args.get('userid'))
    team_id = request.args.get('teamid', 0)
    team_id = int(team_id) if team_id else None

    if team_id:
        project = Project.query.filter_by(
            id=id,
            team_id=team_id
        ).first()
    else:
        project = Project.query.filter_by(
            created_by=user,
            id=id
        ).first()

    completed = []
    incomplete = []

    for obj in Objective.query.filter_by(project_id=project.id).all():
        if obj.isdone: completed.append(obj)
        else: incomplete.append(obj)

    return jsonify({
        'completed': len(completed),
        'incomplete': len(incomplete)
    })

# & Route to get member contribution
@api.route('/team/members/contribution')
def get_contribution():
    team_id = request.args.get('team_id')
    team = Team.query.filter_by(id=int(team_id)).first()
    contribution = {
        'status': 200,
        'message': '',
        'members': [],
        'contribution': [],
    }

    if not team:
        return jsonify({
            'status': 404,
            'message': 'Team not found!',
            'members': [],
            'contribution': [],
        })
    
    for member in Member.query.filter_by(team_id=team.id).all():
        contribution['members'].append(member.mem_name)
        contribution['contribution'].append(member.contribution)

    return jsonify(contribution)

# & Route to get user settings
@api.route('/user-settings/')
def get_user_settings():
    user_id = request.args.get('user-id', 0)
    user_id = int(user_id)
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    social_links = SocialLink.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        'appearance': {
            'theme': settings.theme,
            'accent': settings.accent,
            'chartColor': settings.chart_color_schemes,
            'chartType': settings.chart_type
        },

        'profile': {
            'skills': settings.skills,
            'workingHours': {
                'from': settings.from_hours.strftime("%H:%M"),
                'to': settings.to_hours.strftime("%H:%M")
            },
            'socialLinks': [link.to_dict() for link in social_links]
        },

        'security': {
            'passwordRotation': settings.password_rotation
        },

        'advanced': {
            'preRelease': settings.pre_release
        }
    })