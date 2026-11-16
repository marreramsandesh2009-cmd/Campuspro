import os
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from config import Config
from extensions import db, login_manager
from models import User, Project, Notification

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip'}
app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)
login_manager.init_app(app)


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapped
    return decorator


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.context_processor
def inject_globals():
    unread = 0
    if current_user.is_authenticated:
        unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return {'unread_notifications': unread, 'today': datetime.now()}


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html', total_projects=Project.query.count(), total_students=User.query.filter_by(role='student').count())


@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for({'student':'student_dashboard','faculty':'faculty_dashboard','admin':'admin_dashboard'}[current_user.role]))


@app.route('/student')
@role_required('student')
def student_dashboard():
    projects = Project.query.filter_by(owner_id=current_user.id).order_by(Project.created_at.desc()).all()
    counts = {'total':len(projects), 'approved':sum(p.status=='Approved' for p in projects), 'review':sum(p.status=='Under Review' for p in projects), 'changes':sum(p.status=='Needs Changes' for p in projects)}
    return render_template('student_dashboard.html', projects=projects, counts=counts)


@app.route('/faculty')
@role_required('faculty')
def faculty_dashboard():
    projects = Project.query.order_by(Project.status.in_(['Submitted','Under Review']).desc(), Project.created_at.desc()).all()
    counts = {'total':len(projects), 'pending':sum(p.status in ('Submitted','Under Review') for p in projects), 'approved':sum(p.status=='Approved' for p in projects), 'changes':sum(p.status=='Needs Changes' for p in projects)}
    return render_template('faculty_dashboard.html', projects=projects, counts=counts)


@app.route('/admin')
@role_required('admin')
def admin_dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    counts = {'students':User.query.filter_by(role='student').count(), 'faculty':User.query.filter_by(role='faculty').count(), 'projects':len(projects), 'pending':sum(p.status in ('Submitted','Under Review') for p in projects)}
    return render_template('admin_dashboard.html', users=users, projects=projects, counts=counts)


@app.route('/projects')
@login_required
def projects():
    query = Project.query
    if current_user.role == 'student':
        query = query.filter_by(owner_id=current_user.id)
    search = request.args.get('q','').strip()
    status = request.args.get('status','').strip()
    if search:
        query = query.filter(or_(Project.title.ilike(f'%{search}%'), Project.tech_stack.ilike(f'%{search}%')))
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=items, search=search, selected_status=status)


@app.route('/projects/new', methods=['GET','POST'])
@role_required('student')
def new_project():
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        abstract = request.form.get('abstract','').strip()
        if not title or not abstract:
            flash('Project title and abstract are required.', 'danger')
            return render_template('project_form.html')
        file = request.files.get('attachment')
        filename = ''
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Unsupported attachment type. Use an image, PDF, Office document or ZIP.', 'danger')
                return render_template('project_form.html')
            safe_name = secure_filename(file.filename)
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        project = Project(title=title, abstract=abstract, tech_stack=request.form.get('tech_stack','').strip(), project_url=request.form.get('project_url','').strip(), attachment=filename, owner_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        flash('Your project has been submitted successfully.', 'success')
        return redirect(url_for('projects'))
    return render_template('project_form.html')


@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = db.get_or_404(Project, project_id)
    if current_user.role == 'student' and project.owner_id != current_user.id:
        abort(403)
    return render_template('project_detail.html', project=project)


@app.route('/projects/<int:project_id>/review', methods=['POST'])
@role_required('faculty','admin')
def review_project(project_id):
    project = db.get_or_404(Project, project_id)
    status = request.form.get('status')
    if status not in {'Under Review','Approved','Needs Changes'}:
        abort(400)
    project.status = status
    project.feedback = request.form.get('feedback','').strip()
    project.faculty_id = current_user.id
    db.session.add(Notification(user_id=project.owner_id, message=f'Your project “{project.title}” is now {status}.'))
    db.session.commit()
    flash('Project review saved and student notified.', 'success')
    return redirect(url_for('project_detail', project_id=project.id))


@app.route('/notifications')
@login_required
def notifications():
    items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for item in items:
        item.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=items)


@app.route('/admin/faculty', methods=['POST'])
@role_required('admin')
def add_faculty():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    department = request.form.get('department', '').strip() or 'Computer Science'
    password = request.form.get('password', '')
    if not name or not email or len(password) < 8:
        flash('Enter a name, email and a password with at least 8 characters.', 'danger')
    elif User.query.filter_by(email=email).first():
        flash('An account with this email already exists.', 'danger')
    else:
        faculty = User(name=name, email=email, department=department, role='faculty')
        faculty.set_password(password)
        db.session.add(faculty)
        db.session.commit()
        flash(f'Faculty account created for {name}.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
@role_required('admin')
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
    else:
        user.is_active_account = not user.is_active_account
        db.session.commit()
        flash('User account updated.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not name or not email or len(password) < 8:
            flash('Enter your name, email and a password with at least 8 characters.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
        else:
            user = User(name=name, email=email, password_hash='', role='student')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Student account created. Please sign in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active_account:
            login_user(user)
            flash(f'Welcome back, {user.name.split()[0]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email/password or inactive account.', 'danger')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have signed out.', 'info')
    return redirect(url_for('index'))


@app.errorhandler(403)
def forbidden(_error):
    return render_template('error.html', code=403, message='You do not have permission to access this page.'), 403


@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database tables created.')


@app.cli.command('create-user')
def create_user():
    """Create faculty/admin accounts from the terminal."""
    import getpass
    db.create_all()
    name = input('Full name: ').strip()
    email = input('Email: ').strip().lower()
    role = input('Role (faculty/admin): ').strip().lower()
    password = getpass.getpass('Password (8+ characters): ')
    if role not in ('faculty','admin') or len(password) < 8 or not name or not email:
        print('Invalid details. Role must be faculty/admin and password must be 8+ characters.')
        return
    if User.query.filter_by(email=email).first():
        print('This email is already registered.')
        return
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f'{role.title()} account created.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
