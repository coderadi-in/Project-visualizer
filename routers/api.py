'''coderadi'''

# ? Importing libraries
from flask import Blueprint, request, jsonify
from extensions import *
from datetime import date

today = date.today()

# ! Building api router
api = Blueprint('api', __name__, url_prefix='/api')

# & Route to get left time to complete project
@api.route('/projects/<int:id>/time-data')
def get_time_data(id):
    user = int(request.args.get('userid', 0))
    team_id = int(request.args.get('teamid', 0))

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
    spent_time = total_time - left_time
    
    spent_time = 0 if spent_time < 0 else spent_time
    left_time = 0 if left_time < 0 else left_time

    return jsonify({
        'spent_time': spent_time,
        'left_time': left_time
    })

# & Route to get tasks overview
@api.route('/projects/<int:id>/task-data')
def get_task_data(id):
    user = int(request.args.get('userid', 0))
    team_id = int(request.args.get('teamid', 0))

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
    team_id = int(request.args.get('team_id', 0))
    team = Team.query.filter_by(id=team_id).first()

    if not team:
        return jsonify({
            'status': 404,
            'members': [],
            'contribution': [],
        })

    contribution = {
        'status': 200,
        'members': [],
        'contribution': [],
    }
    
    for member in Member.query.filter_by(team_id=team.id).all():
        contribution['members'].append(member.mem_name)
        contribution['contribution'].append(member.contribution)

    return jsonify(contribution)

# & Route to get user settings
@api.route('/user-settings/')
def get_user_settings():
    user_id = int(request.args.get('user-id', 0))
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