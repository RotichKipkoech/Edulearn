from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime  # Import datetime for handling timestamps

db = SQLAlchemy()

# Association table for many-to-many relationship (Student-Lesson)
student_lessons = db.Table('student_lessons',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    # Relationship: One-to-many with Assignment (Instructor)
    assignments = db.relationship('Assignment', backref='instructor_assignments', foreign_keys='Assignment.instructor_id', lazy=True)

    # Relationship: One-to-many with Assignment (Student)
    student_assignments = db.relationship('Assignment', foreign_keys='Assignment.student_id', backref='student_assignments_link', lazy=True)

    # Relationship: One-to-many with Lesson (Instructor)
    lessons = db.relationship('Lesson', foreign_keys='Lesson.instructor_id', backref='instructor_lessons', lazy=True)

    # Relationship: Many-to-many with Lesson (Student)
    student_lessons = db.relationship('Lesson', secondary=student_lessons, backref=db.backref('enrolled_students', lazy=True), lazy='dynamic')




class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)  # Due date for the assignment
    status = db.Column(db.String(50), nullable=False, default='In Progress')  # Status of the assignment
    grade = db.Column(db.Float, nullable=True)  # Store grade (if available)
    
    # Foreign keys to associate the assignment with an instructor and optionally a student
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Instructor
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Student (optional)

    # Relationships: Each assignment is linked to one instructor and optionally one student
    instructor = db.relationship('User', foreign_keys=[instructor_id], backref='instructor_assignments')  # Instructor reference
    student = db.relationship('User', foreign_keys=[student_id], backref='student_assignments_link', lazy=True)  # Student reference

    # Fields for assignment submission and grading
    submission = db.Column(db.Text, nullable=True)  # Student's submission text
    submitted_on = db.Column(db.DateTime, nullable=True)  # Date of submission
    graded_on = db.Column(db.DateTime, nullable=True)  # Date the assignment was graded

    def __repr__(self):
        return f'<Assignment {self.title}>'



# Lesson Model
class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    # Foreign key to associate the lesson with an instructor
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship: Each lesson is linked to one instructor
    instructor = db.relationship('User', foreign_keys=[instructor_id], backref='instructor_lessons')

    # Relationship: Many-to-many with User (students)
    students = db.relationship('User', secondary=student_lessons, backref=db.backref('student_lessons_link', lazy='dynamic'), lazy='dynamic')

    def __init__(self, title, content, description, due_date, instructor_id):
        self.title = title
        self.content = content
        self.description = description
        self.due_date = due_date
        self.instructor_id = instructor_id


