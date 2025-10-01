'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, abort, redirect, flash, url_for, request, send_from_directory
from datetime import date, timedelta
from extensions import *

# ! Building admin router
admin = Blueprint('admin', __name__, url_prefix='/admin')

# & Socket listener for seenBtn click
@socket.on('mark-feed')
def delete_feed(data):
    feed = Feed.query.get(data['feedId'])
    db.session.delete(feed)
    db.session.commit()
    socket.emit('mark-feed-callback', {'feedId': data['feedId']})

# * Helper function to check if viewer is admin
def check_admin():
    if (not current_user.is_authenticated) or (current_user.email != os.getenv('ADMIN_EMAIL')): abort(404)

# | Context processor
@admin.context_processor
def inject_common_vars():
    settings = UserSettings.query.filter_by(user_id=current_user.id).first()

    return {
        'theme': settings.theme,
        'accent': settings.accent
    }

# & Panel route
@admin.route('/panel')
@login_required
def panel():
    check_admin()

    hosting = Hosting.query.first()
    today = date.today()
    feeds = Feed.query.all() if (Feed.query.count() > 0) else None

    data = {
        'total_users': User.query.count(),
        'total_teams': Team.query.count(),
        'total_projects': Project.query.count(),
        'total_subscriptions': Subscription.query.count(),
        'membership_pass': 0,
        'membership_income': 0,
        'hosting_left': (hosting.end_date - today).days,
        'hosting_charge': hosting.charge,
        'feeds': feeds
    }

    return render_template('admin/panel.html', data=data)

# & Database page route
@admin.route('/database')
@login_required
def database():
    check_admin()

    db_size = (os.path.getsize('instance/visualizer.sqlite3') / 1024) / 1024
    db_size = round(db_size, 2)

    db_tables = {}
    with db.engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ))
        tables = [row[0] for row in result]
        db_count = len(tables)

        for table in tables:
            cols = conn.execute(text(f"PRAGMA table_info({table});")).fetchall()
            columns = [{
                'name': col[1],
                'type': col[2],
                'class': 'primary' if col[5] == 1 else 'secondary'
            } for col in cols]

            db_tables[table] = {
                'data': {'name': table.capitalize()},
                'columns': columns
            }

    return render_template('admin/db.html', data={
        'db_count': db_count,
        'db_size': db_size,
        'db_tables': db_tables
    })

# & Notify route
@admin.route('/notify', methods=['POST'])
def notify():
    title = request.form.get('title')
    msg = request.form.get('msg')
    attachment = request.form.get('attachment')

    new_notficiation = Notification(
        title=title,
        message=msg,
        recv=0,
        attachment=attachment,
        badge='app'
    )

    db.session.add(new_notficiation)
    db.session.commit()

    flash("Notification has been added.", "success")
    return redirect(url_for('admin.panel'))

# & Add newsletter route
@admin.route('/newsletter', methods=['POST'])
def newsletter():
    title = request.form.get('title')
    content = request.form.get('content')
    recipients = [user.email for user in Subscription.query.all()]

    msg = Message(
        subject=title,
        body=content,
        recipients=recipients,
    )
    mail.send(msg)

    flash("Newsletter sent successfully.", 'success')
    return redirect(url_for('admin.panel'))

# & Download db route
@admin.route('/download_db', methods=['POST'])
def download_db():
    admin_pass = request.form.get('password')

    if (admin_pass == os.getenv('ADMIN_PASS')):
        return send_from_directory(
            directory="instance",
            path="visualizer.sqlite3",
            as_attachment=True
        )
    
    flash("Invalid ADMIN PASSKEY!")
    return redirect(url_for('auth.logout'))

# & Upload db route
@admin.route('/upload_db', methods=['POST'])
def upload_db():
    admin_pass = request.form.get('password')

    if (admin_pass == os.getenv('ADMIN_PASS')):
        db_file = request.files.get('db_file')
        
        if db_file:
            filename = secure_filename(filename="visualizer.sqlite3")
            db_path = os.path.join(current_app.instance_path, filename)
            db_file.save(db_path)

            flash("Database has beed updated.", "success")
            return redirect(url_for('admin.database'))
    
    else:
        flash("Invalid ADMIN PASSKEY!", "error")
        return redirect(url_for('auth.logout'))
    
# & Renew hosting route
@admin.route('/renew')
def renew():
    hosting = Hosting.query.first()

    hosting.start_date = date.today()
    hosting.end_date = date.today() + timedelta(days=30)
    db.session.commit()

    flash("Hosting has beed updated.", "success")
    return redirect(url_for('admin.panel'))