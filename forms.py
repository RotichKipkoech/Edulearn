from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

# Login form for users to log in
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Form for creating a new user (for admin)
class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('INSTRUCTOR', 'Instructor'), ('STUDENT', 'Student')], validators=[DataRequired()])
    submit = SubmitField('Create User')

# Form for creating a lesson (for instructor)
class CreateLessonForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Lesson')

class CreateAssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])  # Updated format
    submit = SubmitField('Create Assignment')

# Form for grading an assignment (for instructor)
class GradeAssignmentForm(FlaskForm):
    grade = StringField('Grade', validators=[DataRequired()])
    submit = SubmitField('Grade Assignment')

# Form for students to submit assignments
class SubmitAssignmentForm(FlaskForm):
    status = SelectField('Status', choices=[('in progress', 'In Progress'), ('submitted', 'Submitted')], validators=[DataRequired()])
    submit = SubmitField('Submit Assignment')
