'''coderadi'''

# ? Importing libraries
from main import *
import json

SKILLS_FILE = 'skills.json' # ! Skills file path
QTY = 0
FOLDERS = [
    'static/public'
]

# ! Creating database
with server.app_context():
    db.create_all()

# & Loading skills data
with open(SKILLS_FILE) as f:
    data = json.load(f)

# ! Updating skills in database
for category in data:
    for skill in data[category]:
        with server.app_context():
            if not (Skill.query.filter_by(skill=skill['hashtag'])).first():
                new_skill = Skill(
                    category=category,
                    skill=skill['hashtag'],
                )
                db.session.add(new_skill)
                db.session.commit()
                QTY += 1
print(f"Added {QTY} skill(s) to db.")

# ! Creating all folders
for folder in FOLDERS:
    os.makedirs(folder, exist_ok=True)

# ! Starting the server
if __name__ == "__main__":

    socket.run(server, debug=False, host='0.0.0.0', allow_unsafe_werkzeug=True)
