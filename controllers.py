from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, abort, make_response, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_migrate import Migrate
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import sqlite3, os, re, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.models import *

controllers = Blueprint('controllers', __name__)

bcrypt = Bcrypt()

# cus will be replaced by stu
#  pro will be replaced by tu
# service will be replaced by classes

# Utility function to validate email
def validate_email(email):
    # Basic email validation using regex
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

# home route
@controllers.route('/', methods=['GET', 'POST'])
def home():
    return render_template('a_home.html')

# login route
@controllers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        # print(user.role)
        if user:
            if check_password_hash(user.password, password):
                if user.role == "student":
                    if user.flag == 0:
                        flash('Logged in successfully as an student', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('controllers.stu_home'))
                    else:
                        flash('User is flagged', category='error')
                        return render_template('login.html')    
                elif user.role == "admin":
                    flash('Logged in successfully as an admin', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('controllers.admin_dash'))
                elif user.role == "tutor":
                    if user.flag == 0 and user.iitEmail:
                        flash('Logged in successfully as a tutor', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('controllers.tu_home'))
                    else:
                        flash('User is flagged, please contact the Admin', category='error')
                        return render_template('login.html')
            else:
                flash('Incorrect password', category='error')
                return render_template('login.html')
        else:
            flash('User does not exist', category='error')
            return render_template('login.html')
    else:
        return render_template("login.html")

# logout route
@controllers.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('controllers.home'))

# sign up route
@controllers.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'student':
            fullName = request.form.get('fullName')
            email = request.form.get('email')
            password = request.form.get('password')
            preferredSubjects = request.form.getlist('preferredSubjects[]')
            grade = request.form.get('grade')
        elif role == 'tutor':    
            fullName = request.form.get('fullName')
            email = request.form.get('email')
            password = request.form.get('password')
            certificates = request.form.get('certificates')
            experience = request.form.get('experience')
            # personalEmail = request.form.get('personalEmail')
            iitEmail = request.form.get('iitEmail')
            mobileNo = request.form.get('mobileNo')
        
        # created_at = datetime.now()

        # created_at = datetime.strptime(created_at, '%Y-%m-%d')

        # Debugging: Print the selected subjects in the console
        print("Selected Subjects:", preferredSubjects)

        # Return a response or render a template with the data
        print(f"You selected: {', '.join(preferredSubjects)}")
        
        if len(fullName) < 5:
            flash('Username must be at least 5 characters', category='error')
            return render_template('signup.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters', category='error')
            return render_template('signup.html')
        
        if password.isalpha():
            flash('Password must contain at least one number', category='error')
            return render_template('signup.html')
        
        if password.isnumeric():
            flash('Password must contain at least one letter', category='error')

        if len(iitEmail) < 10 and len(email) < 10:
            flash('Email must be at least 10 characters', category='error')
            return render_template('signup.html')
        
        if iitEmail.count('@') != 1 and email.count('@') != 1:
            flash('Email must contain @', category='error')
            return render_template('signup.html')
        if iitEmail.count('.') == 0 and email.count('.') == 0:
            flash('Email must contain .', category='error')
            return render_template('signup.html')

        if role == "student":
            if Users.query.filter_by(fullName=fullName).first():
                flash('Username already exists', category='error')
                return render_template('signup.html')
            elif Users.query.filter_by(email=email).first():
                flash('Email already exists', category='error')
                return render_template('signup.html')
            else:
                user = Users(name=fullName, email=email, role=role, grade=grade, Subjects=preferredSubjects,
                     password=generate_password_hash(password, method='sha256'))
                db.session.add(user)
                db.session.commit()

        elif role == "tutor":
            if Users.query.filter_by(fullName=fullName).first():
                flash('Username already exists', category='error')
                return render_template('signup.html')
            elif Users.query.filter_by(iitEmail=iitEmail).first():
                flash('Email already exists', category='error')
                return render_template('signup.html')
            else:
                user = Users(name=fullName, email=email, contact_no = mobileNo, role=role, experience=experience,iitEmail=iitEmail, 
                             certificates = certificates,
                             password=generate_password_hash(password, method='sha256'))
                db.session.add(user)
                db.session.commit()        
        flash('Account created successfully', category='success')
        return redirect(url_for('controllers.login'))
    
    else:
        flash('Please fill the form', category='warning')
        return render_template('signup.html')

# contact us route
@controllers.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        contact_no = request.form.get('contact_no')
        message = request.form.get('message')
        created_at = datetime.now()
        
        created_at = datetime.strptime(created_at, '%Y-%m-%d')

        contact_us = ContactUs(name=name, email=email, message=message, contact_no=contact_no, created_at=created_at)
        db.session.add(contact_us)
        db.session.commit()
        flash('Message sent successfully', category='success')
        return redirect(url_for('controllers.contact_us'))
    else:
        return render_template('contact_us.html')


# forgot password route
@controllers.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Users.query.filter_by(email=email).first()
        if not user:
            flash('Email does not exist', category='error')
            return redirect(url_for('controllers.home'))
        # else:
        #     token = s.dumps(email, salt='email-confirm') # #4caf50
        #     msg = Message('Confirm Email', sender='noreply@demo.com', recipients=[email])
        #     link = url_for('controllers.reset_password', token=token, _external=True)   
        #     msg.body = 'Your link is {}'.format(link)   
        #     mail.send(msg)   
        #     flash('Check your email for a password reset link', category='success')
        else:
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash('Passwords do not match', category='error')
                return render_template('a_forgot_pswd.html')
            else:
                user.password = generate_password_hash(new_password, method='sha256')
                db.session.commit()
                flash('Password reset successful', category='success')
                return redirect(url_for('controllers.login'))
    else:
        return render_template('a_forgot_pswd.html')
    
# user profile route 
# (TBD)
@controllers.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    email = current_user.email
    user = Users.query.filter_by(email=email).first()
    return render_template('tu_profile.html', Username = user.name, role = user.role,
                           email = user.email, contact_no = user.contact_no, dob=user.dob,
                           preferred_service_location = user.preferred_service_location
                        #    address = user.address,
                        #    city = user.city, state = user.state, pincode = user.pincode,
                        #    bio = user.bio
                           )

# admin dashboard route
@controllers.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
def admin_dash():
    if current_user.role == 'Admin':
        user = Users.query.all()
        classes = MentorshipPrograms.query.all()
        return render_template('ad_dash.html', Username = current_user, user = user, classes = classes)
    else:
        flash('You are not authorized to view this page', category='error')
        return redirect(url_for('controllers.home'))

# FLAG and UNFLAG, BLOCK and UNBLOCK ROUTES
# Flag route
@controllers.route("/flag/<int:user_id>", methods=["GET", "POST"])
@login_required
def flag(user_id):
    print(user_id)
    try:
        user = Users.query.filter_by(id=user_id).first()
        if user:
            if user.flag == 0:
                user.flag = 1
            db.session.commit()  # Commit changes
            db.session.close()
            flash("User has been FLAGGED", category="success")
        else:
            flash("User not found!", category="error")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        flash("Database error: " + str(e), category="error")
    finally:
        db.session.close()  # Ensure session is closed
        
    return redirect(url_for('admin_dash'))  # Redirect after the operation
    
    flash("Something is wrong!!", category="error")
    return redirect(url_for('admin_dash'))

# Unflag route
@controllers.route("/unflag/<int:user_id>", methods=["GET", "POST"])
@login_required
def unflag(user_id):
    user = Users.query.filter_by(id=user_id).first()
    if user:
        if user.flag == 1:
            user.flag = 0
        db.session.commit()
        db.session.close()
        flash("Unflagged Successfully",category="success")
        return redirect (url_for('admin_dash'))
    else:
        flash("Something went wrong!",category="error")
        return redirect (url_for('admin_dash'))    

# add service by admin
@controllers.route("/add_service", methods=["GET", "POST"])        
@login_required
def add_service():
    if request.method == "POST":
        service_name = request.form.get("service_name")
        subjects = request.form.get("subjects")
        category = request.form.get("service_price")
        base_price = request.form.get("service_duration")
        # service_image = request.files.get("service_image")
        # service_image_path = None
        # if service_image:
        #     filename = secure_filename(service_image.filename)
        #     service_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #     service_image.save(service_image_path)
        service = MentorshipPrograms(title=service_name, description=subjects, budget=category, price=base_price)
        db.session.add(service)
        db.session.commit()
        flash("Service added successfully!", category="success")
        return redirect(url_for('admin_dash'))
    return render_template("add_service.html")


# ROUTES FOR Tutors
# tu_home route
@controllers.route("/tu_home", methods = ["GET","POST"])
@login_required
def tu_home():
    user_id = current_user.id
    name = current_user.name
    services =  Appointments.query.get(user_id)
    # service_requests = ServiceRequest.query.filter_by(professional_id = current_user.id).all()
    return render_template("tu_home.html", services = services, 
                           name = name)

# tu_search route
@controllers.route("/tu_search", methods = ["GET","POST"])
@login_required
def tu_search():
    if request.method == "POST":
        query = request.form.get("searchText")
        filter = request.form.get("searchBy")
        if filter == "service-name":
            services = Service.query.filter(Service.service_name.ilike(f"%{query}%")).all()
            print(services)
            if services:
                return render_template("pro_search.html", services=services)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        elif filter == "pincode":
            service_requests = ServiceRequest.query.filter(ServiceRequest.pincode.like(f"%{query}%")).all()
            print(service_requests)
            if service_requests:
                return render_template("pro_search.html", service_requests=service_requests)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        elif filter == "status":
            service_requests = ServiceRequest.query.filter(ServiceRequest.service_status.like(f"%{query}%")).all()
            # print(service_requests)
            if service_requests:
                return render_template("pro_search.html", service_requests=service_requests)
            else:
                flash("No services found", category="error")
                return render_template("pro_search.html")
        else:
            services = ServiceRequest.query.all()
            return render_template("pro_search.html", services=services)
    else:
        return render_template("pro_search.html")
    
# tu_complete route
@controllers.route("/tu_complete/<int:service_id>", methods=["GET", "POST"])
@login_required
def pro_complete(service_id):
    service = Appointments.query.get(service_id)
    if service:
        if request.method == "POST":
            if Appointments.status == "Pending":
                service.service_status = "Closed"
                db.session.commit()
                db.session.close()
                flash("Marked as completed!", category="success")
                return redirect(url_for('tu_home'))
        else:
            return render_template("pro_complete.html", service=service, service_id=service_id)
    else:
        flash("Service not found", category="error")
        return redirect(url_for('tu_home'))

# mark_as_complete route
# @controllers.route("/mark_as_complete/<int:service_id>", methods=["GET", "POST"])
# @login_required
# def mark_as_complete(service_id):
#     service = ServiceRequest.query.get(service_id)
#     if service:
#         if request.method == "POST":
#             if service.service_status == "Requested" or service.service_status == "Assigned":
#                 service.service_status = "Closed"
#                 db.session.commit()
#                 db.session.close()
#                 flash("Service marked as completed!", category="success")
#                 return redirect(url_for('cus_home'))
#         else:
#             return render_template("mark_as_complete.html", service=service, service_id=service_id)
#     else:
#         flash("Service not found", category="error")
#         return redirect(url_for('cus_home'))        

# ROUTES FOR STUDENTS

@controllers.route("/review", methods = ["GET","POST"])
@login_required
def review():
    if request.method == "POST":
        service_id = request.form.get("service_id")
        rating = request.form.get("rating")
        review_text = request.form.get("review_text")
        review = Review(service_id=service_id, rating=rating, review_text=review_text)
        db.session.add(review)
        db.session.commit()
        flash("Review added successfully!", category="success")
        return redirect(url_for('review'))
    else:
        return render_template("stu_review.html")

# cus_home route
@controllers.route("/stu_home", methods = ["GET","POST"])
@login_required
def stu_home():
    services = Service.query.all()
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    # print(current_user.id)
    return render_template("stu_home.html",services = services, name = current_user.name,
                           service_requests = service_requests)

# cus_search route
@controllers.route("/stu_search", methods = ["GET","POST"])
def cus_search():
    if request.method == "POST":
        query = request.form.get("searchText")
        filter = request.form.get("searchBy")
        if filter == "service-name":
            services = Service.query.filter(Service.service_name.ilike(f"%{query}%")).all()
            print(services)
            if services:
                return render_template("cus_search.html", services=services)
            else:
                flash("No services found with this spectification.", category="error")
                return render_template("cus_search.html")
        elif filter == "pincode":
            services = Service.query.filter(Service.pincode.like(f"%{query}%")).all()
            # flash("No services found for this pincode.", category="error")
            return render_template("cus_search.html", services=services)
        elif filter == "status":
            service_requests = ServiceRequest.query.filter(ServiceRequest.service_status.like(f"%{query}%")).all()
            # flash("No service requests found with this spectification.", category="error")
            return render_template("cus_search.html", service_requests=service_requests)
        else:
            services = Service.query.all()
            flash("No services found with this spectification.", category="error")
            return render_template("cus_search.html", services=services)
    else:
        return render_template("cus_search.html")

# cus_summary route
@controllers.route("/stu_summary", methods = ["GET","POST"])
@login_required
def cus_summary():
    return render_template("cus_summary.html")

# stu_review route
@controllers.route("/stu_review", methods = ["GET","POST"])
@login_required
def stu_review():
    return render_template("stu_review.html")

# payments route
@controllers.route("/payments", methods = ["GET","POST"])
@login_required
def payments():
    return render_template("payments.html")

@controllers.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    # Process payment logic here, if any
    cardNumber = request.get("cardNumber")
    expiryDate = request.get("expiryDate")
    cvv = request.get("cvv")
    
    if cardNumber:
        if expiryDate:
            if cvv:
                # Payment successful, redirect to a confirmation page
                flash("Payment Completed! Please visit the Home Page to check your booked services.")
                return redirect(url_for('payment_cnf'))
            else:
                flash("Please enter the CVV.", category="error")
                return redirect(url_for('payments'))
        else:
            flash("Please enter the expiry date.", category="error")
            return redirect(url_for('payments'))
    else:
        flash("Please enter the card number.", category="error")
        return redirect(url_for('payments'))

    # flash("Payment Completed! Please visit the Home Page to check your booked services.")
    # return redirect(url_for('payment_cnf'))

@controllers.route('/payment_cnf', methods=['GET'])
@login_required
def payment_cnf():
    return render_template('payment_cnf.html')

# cus_book_service route
@controllers.route("/stu_book_class/<int:service_id>", methods=["GET", "POST"])
@login_required  
def stu_book_class(service_id):
    if request.method == "POST":
        if current_user.role == "student":
            # Retrieve current user's ID
            user_id = current_user.id
            
            # Collect form data
            description = request.form.get("description")
            pincode = request.form.get("pincode")
            base_price = request.form.get("payment_amount")
            date_of_request = request.form.get("date_of_request")
            date_of_completion = request.form.get("date_of_completion")
            remarks = request.form.get("remarks")
            date_of_request = datetime.strptime(date_of_request, '%Y-%m-%d')
            date_of_completion = datetime.strptime(date_of_completion, '%Y-%m-%d')
            # Assuming you have a ServiceRequest model to store the booking information
            appointments = Appointments(student_id=user_id, mentor_id=service_id, program_id=service_id, date=date_of_request, 
                                        time=date_of_completion)
        
            # Save the booking in the database
            db.session.add(appointments)
            db.session.commit()
            db.session.close()
            flash("Class booked successfully!", category="success")
            return redirect(url_for('student_checkout'))
    else:
        service = MentorshipPrograms.query.get(service_id)
        return render_template("cus_book_service.html", service_id=service_id, service=service)
    
# student checkout route
@controllers.route("/student_checkout/<int:service_id>", methods=["GET", "POST"])
@login_required
def student_checkout(service_id):
    service = ServiceRequest.query.get(service_id)
    return render_template("student_checkout.html", service_id=service_id, service=service)

            
@controllers.route("/cus_serv_change_status/<int:service_id>", methods=["GET", "POST"])
@login_required
def cus_serv_change_status(service_id):
    service = ServiceRequest.query.get(service_id)
    if service:
        if request.method == "POST":
            if service.service_status == "Rejected":
                service.service_status = "Requested"
                db.session.commit()
                db.session.close()
                flash("Service status updated successfully!", category="success")
                return redirect(url_for('cus_home'))
            else:
                flash("Service status cannot be changed!", category="error")
                return redirect(url_for('cus_home'))
        else:
            return render_template("cus_home.html", service=service, service_id=service_id)
    else:
        flash("Service status cannot be changed!", category="error")
        return redirect(url_for('cus_home'))

# EDIT AND DELETE SERVICE ROUTES

#Edit service route 
# TBD
@controllers.route("/edit_service/<int:service_id>", methods=["GET","POST"])
@login_required
def edit_service(service_id):
    if request.method == "POST":
        service_name = request.form.get("service_name")
        description = request.form.get("description")
        base_price = request.form.get("base_price")
        pincode = request.form.get("pincode")
        service = Service.query.filter_by(id=service_id).first()
        if service:
            if service_name:
                service.service_name = service_name
            if description:
                service.description = description
            # if pincode:
            #     service.pincode = pincode
            if base_price:
                service.budget = base_price
            db.session.commit()
            db.session.close()
            flash("Service updated successfully!", category="success")
            return redirect(url_for('admin_dash'))
        else:
            flash("Service not found!", category="error")
            return render_template('admin_dash.html', service_id = service_id)
    else:    
        service = Service.query.filter_by(id=service_id).first()
        service_name = service.service_name
        description = service.description
        budget = service.budget
        pincode = service.pincode
        return render_template("ad_edit_service.html", service_id = service_id,
                               service_name = service_name, description = description, 
                               pincode=pincode, budget = budget) 


# #Delete service route
# @controllers.route("/delete_service/<int:service_id>", methods=["GET","POST"])
# @login_required
# def delete_service(service_id):
#     if request.method == "POST":
#         print ("Service id: ", service_id)
#         service = Service.query.filter_by(id = service_id).first()
#         print ("Service: ", service)
#         if service:
#             db.session.delete(service)
#             db.session.commit()
#             db.session.close()
#             flash("Service deleted successfully!", category="success")
#             return redirect(url_for('admin_dash'))
#         else:
#             flash("Service not found!", category="error")
#             return redirect(url_for('admin_dash', service_id = service_id))
#     else:
        
#         return redirect(url_for('admin_dash'))

