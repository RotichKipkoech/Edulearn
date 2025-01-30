from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import LoginForm, CreateUserForm, CreateLessonForm, CreateAssignmentForm
from flask_migrate import Migrate
from models import db, User, Assignment, Lesson

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'  # Change this to something secure for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduleaner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to login if they are not authenticated

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create the database tables
with app.app_context():
    db.create_all()

# Automatically create Admin user if it doesn't exist
with app.app_context():
    admin = User.query.filter_by(username="ADM-001").first()
    if not admin:
        admin = User(username="ADM-001", password=generate_password_hash("Admin@123"), role="ADMIN")
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        # If the user is already logged in, redirect them to their dashboard
        if current_user.role == 'ADMIN':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'INSTRUCTOR':
            return redirect(url_for('instructor_dashboard'))
        elif current_user.role == 'STUDENT':
            return redirect(url_for('student_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            next_page = request.args.get('next')  # Get the page they were trying to access before login
            if not next_page:
                if user.role == 'ADMIN':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'INSTRUCTOR':
                    return redirect(url_for('instructor_dashboard'))
                elif user.role == 'STUDENT':
                    return redirect(url_for('student_dashboard'))
            return redirect(next_page)

        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)




@app.route('/logout')
@login_required
def logout():
    logout_user()  # Flask-Login handles session logout
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Only allow access to admin users
    if current_user.role != 'ADMIN':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    users = User.query.all()  # Get the list of users
    
    # Handle the POST request for user creation
    form = CreateUserForm()  # Instantiate the form
    
    if form.validate_on_submit():  # Check if the form is valid
        username = form.username.data
        password = form.password.data
        role = form.role.data
        
        hashed_password = generate_password_hash(password)  # Generate a hashed password
        new_user = User(username=username, password=hashed_password, role=role)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to reload the dashboard

    return render_template('admin_dashboard.html', users=users, form=form)  # Pass the form to the template



@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    # Only allow access to admin users
    if current_user.role != 'ADMIN':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    form = CreateUserForm()  # Instantiate the form

    if form.validate_on_submit():  # Check if the form is valid on submission
        username = form.username.data
        password = form.password.data
        role = form.role.data

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(password)

        # Create the new user
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard after successful creation

    return render_template('create_user.html', form=form)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'ADMIN':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.password = generate_password_hash(request.form['password'])
        user.role = request.form['role']
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if current_user.role != 'ADMIN':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


# Instructor routes
@app.route('/instructor_dashboard', methods=['GET', 'POST'])
@login_required
def instructor_dashboard():
    if current_user.role != 'INSTRUCTOR':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    # Get all assignments created by the instructor (assigned to students)
    assignments = Assignment.query.filter_by(instructor_id=current_user.id).all()

    # Handle grading and status update (POST request)
    if request.method == 'POST':
        assignment_id = request.form.get('assignment_id')
        grade = request.form.get('grade')
        status = request.form.get('status')

        # Get the assignment and update its status and grade
        assignment = Assignment.query.get(assignment_id)
        if assignment:
            assignment.grade = grade
            assignment.status = status
            db.session.commit()
            flash('Assignment graded successfully and status updated!', 'success')

        return redirect(url_for('instructor_dashboard'))

    return render_template('instructor_dashboard.html', assignments=assignments)



@app.route('/create_lesson', methods=['GET', 'POST'])
@login_required
def create_lesson():
    if current_user.role != 'INSTRUCTOR':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    form = CreateLessonForm()  # Instantiate the form

    if form.validate_on_submit():  # Check if the form is valid
        title = form.title.data
        content = form.content.data

        # Logic to create a new lesson
        new_lesson = Lesson(title=title, content=content, instructor_id=current_user.id)
        db.session.add(new_lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('instructor_dashboard'))  # Redirect to the instructor dashboard

    return render_template('create_lesson.html', form=form)  # Pass the form to the template


@app.route('/create_assignment', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role != 'INSTRUCTOR':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    form = CreateAssignmentForm()

    if form.validate_on_submit():  # If the form is valid
        title = form.title.data
        description = form.description.data
        due_date = form.due_date.data

        print(f"Form data: {form.data}")  # Add this line to debug form data

        # Logic to create a new assignment
        new_assignment = Assignment(title=title, description=description, due_date=due_date, instructor_id=current_user.id)
        db.session.add(new_assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('instructor_dashboard'))  # Redirect to the instructor dashboard after creation
    else:
        # Print out the form errors
        print(f"Form errors: {form.errors}")  # Add this to debug form validation errors

    return render_template('create_assignment.html', form=form)


@app.route('/grade_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def grade_assignment(assignment_id):
    if current_user.role != 'INSTRUCTOR':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    assignment = Assignment.query.get(assignment_id)

    if request.method == 'POST':
        grade = request.form['grade']
        assignment.grade = grade
        assignment.status = 'graded'
        db.session.commit()
        flash('Assignment graded successfully!', 'success')
        return redirect(url_for('instructor_dashboard'))

    return render_template('grade_assignment.html', assignment=assignment)


# Student routes
@app.route('/student_dashboard', methods=['GET'])
@login_required
def student_dashboard():
    if current_user.role != 'STUDENT':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    # Get all assignments that are assigned to this student
    assignments = Assignment.query.all()

    # Get all lessons created by this instructor (if this is an instructor role; can be customized)
    lessons = Lesson.query.all()  # Optionally filter lessons based on instructor

    return render_template('student_dashboard.html', assignments=assignments, lessons=lessons)



@app.route('/submit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    if current_user.role != 'STUDENT':
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('index'))

    assignment = Assignment.query.get(assignment_id)

    if request.method == 'POST':
        assignment.status = 'in progress'
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('submit_assignment.html', assignment=assignment)


if __name__ == '__main__':
    app.run(debug=True)
