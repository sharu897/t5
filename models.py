from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# -- Users Table
class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    # common columns
    user_id = db.Column(db.Integer, primary_key=True)  
    fullName = db.Column(db.String(100), nullable=False)  
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password = db.Column(db.String(100), nullable=False) 

    # columns for different roles
    role = db.Column(db.String(100), nullable=False) 

    # -- For Students
    preferredSubjects = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(100), nullable=True)

    # -- For Tutors
    certificates = db.Column(db.String(300), nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    personalEmail = db.Column(db.String(100), nullable=True)
    iitEmail = db.Column(db.String(100), nullable=True)
    contact_no = db.Column(db.String(15), nullable=True) 
    category = db.Column(db.String(100), nullable=True)
    
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)
    flag = db.Column(db.Boolean, nullable=False ,default=False)

# -- Mentorship Programs Table
class MentorshipPrograms(db.Model): 
    __tablename__ = 'mentorship_programs'
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(100), nullable=False)  
    description = db.Column(db.String(500), nullable=False)  
    budget = db.Column(db.Float)
    # duration = db.Column(db.Integer)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -- Appointments Table
class Appointments(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)  
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('mentorship_programs.program_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -- Feedback Table
class Feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -- Messages Table
class Messages(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)  
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

# -- Payments Table
class Payments(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('mentorship_programs.program_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')

# -- Contact Us Table
class ContactUs(db.Model):
        __tablename__ = 'contact_us'
        contact_id = db.Column(db.Integer, primary_key=True)  
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), nullable=False)  
        contact_no = db.Column(db.String(15), nullable=False)
        message = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        

