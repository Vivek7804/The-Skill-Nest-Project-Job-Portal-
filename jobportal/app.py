import os
from flask import Blueprint, Flask, current_app, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import flash, redirect, url_for
from flask import session
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message


# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Folder to store uploaded resumes
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt'}

# Configure the secret key for sessions and flash messages
app.secret_key = 'vs07'

# Configure the database URI (using MySQL with MySQL Connector)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/jobportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Port for TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'skillnestteam@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'jmtk vrti dknk vgxp'  # Your Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'skillnestteam@gmail.com'  # Your email address
app.config['MAIL_DEBUG'] = True

mail = Mail(app)
reports_bp = Blueprint('reports', __name__)

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

class EmailLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message = db.Column(db.Text, nullable=False)

    user = db.relationship('User', backref=db.backref('email_logs', lazy=True))

    def __repr__(self):
        return f'<EmailLog {self.id} - {self.username}>'

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)  # Store the username here as before
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add user_id column
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
    user = db.relationship('User', backref='applications', lazy=True)  # Relationship with User

    def __repr__(self):
        return f"<JobApplication {self.id}>"
    
from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=True, unique=True)
    password = db.Column(db.String(100), nullable=False)  # Hashed password
    role = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    # Hash the password before saving it
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if a password matches the hashed password
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    job_status = db.Column(db.String(50), nullable=False)
    qualifications = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Integer, nullable=True)
    vacancy = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    salary = db.Column(db.Numeric(10, 2), nullable=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to User

    recruiter = db.relationship('User', backref='jobs', lazy=True)  # Relationship with User

    def __repr__(self):
        return f'<Job {self.title}>'

class SavedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # Add this line for is_read
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification {self.id}>"
    
class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)  # Fix typo: compan_name -> company_name
    role = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<WorkExperience {self.company_name}, {self.role}, {self.job_title}>'

class Resume(db.Model):
    __tablename__ = 'resume'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship with User model
    user = db.relationship('User', backref='resumes')

    def __repr__(self):
        return f"<Resume(id={self.id}, resume={self.resume}, created_at={self.created_at})>"

class Education(db.Model):
    __tablename__ = 'education'
    education_id = db.Column(db.Integer, primary_key=True)  # Auto-incremented primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User table
    degree = db.Column(db.String(255), nullable=False)  # Degree name (e.g., Bachelors, Masters)
    institution = db.Column(db.String(255), nullable=False)  # Institution name
    year_of_passing = db.Column(db.Integer, nullable=False)  # Year of graduation
    tenth = db.Column(db.String(50), nullable=True)  # Tenth grade details
    twelfth = db.Column(db.String(50), nullable=True)  # Twelfth grade details

    # Relationship to User (allows access to user's education from User object)
    user = db.relationship('User', backref='education')

    def __repr__(self):
        return f"<Education(degree={self.degree}, institution={self.institution}, year_of_passing={self.year_of_passing})>"
class skills(db.Model):
    __tablename__ = 'skills'  # Explicitly naming the table as 'skills'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Feedback(name={self.name}, email={self.email}, feedback_type={self.feedback_type})>"


# Directory to store uploaded files
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Routes
@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/home')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/jobs')
def job_list():
    jobs = Job.query.all()  # Fetch all jobs
    return render_template('manage_job.html', jobs=jobs)

@app.route('/job_detail/<int:job_id>')
def job_detail(job_id):
    # Fetch the job using the provided job ID
    job = Job.query.get_or_404(job_id)
    # Pass the job details to the template
    return render_template('job_detail.html', job=job)

@app.route('/learn_more')
def learn():
    return render_template('learn_more.html')

#for notifications
@app.route('/notify')
def notify():
    return render_template('notify.html')




@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'username' in session:
        return redirect(url_for('dashboard'))  # Redirect to dashboard if already logged in

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Ensure both fields are provided
        if not username or not password:
            flash('Username and password are required.', 'warning')
            return redirect(url_for('signin'))

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):  # Use the check_password method
            # Log in the user and set session variables
            session['username'] = username
            session['role'] = user.role  # Assuming your `User` model has a `role` field
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('signin.html')


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']

        # Add the user to the database
        new_user = User(username=username, password=password, role=role, email=email)
        new_user.set_password(password)  # Hashing the password
        db.session.add(new_user)
        db.session.commit()

        # Send a welcome email
        try:
            msg = Message(
            subject="Welcome to Our Platform!",
            recipients=[email],  # Email entered during registration
            body=f"""
            Hello {username}! 🎉

            We are thrilled to have you as part of our community. 🚀

            Get ready to explore amazing features and make the most of your experience with us.

            To get started, click the link below:
            
            Go to Dashboard: http://192.168.38.50:5050/signin

            If you have any questions, feel free to contact us.
            
            Happy exploring! 😊
            """
        )
            mail.send(msg)
            flash('Signup successful! A welcome email has been sent.', 'success')

            # Log the email details in the database
            email_log = EmailLog(
                user_id=new_user.id,
                username=username,
                email=email,
                message=msg.body,  # Storing the email body
                sent_at=datetime.utcnow()  # Storing the current timestamp
            )
            db.session.add(email_log)
            db.session.commit()

        except Exception as e:
            flash(f'Signup successful, but failed to send email: {e}', 'warning')

        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/view_email_logs')
def view_email_logs():
    # Retrieve email logs (filter by user or as needed)
    email_logs = EmailLog.query.all()

    return render_template('email_logs.html', email_logs=email_logs)


# Save a job using session
@app.route('/save_job/<int:job_id>', methods=['POST'])
def save_job_view(job_id):
    if 'username' not in session:
        flash('Please log in to save jobs.', 'warning')
        return redirect(url_for('signin'))

    # Get the logged-in user's ID
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('signin'))

    job = Job.query.get_or_404(job_id)

    # Check if the job is already saved by the user
    existing_saved_job = SavedJob.query.filter_by(user_id=user.id, job_id=job.id).first()
    if existing_saved_job:
        flash('You have already saved this job.', 'info')
    else:
        # Save the job to the database
        new_saved_job = SavedJob(
            user_id=user.id,
            job_id=job.id,
            title=job.title,
            location=job.location,
            job_type=job.job_type,
            photo=job.photo
        )
        db.session.add(new_saved_job)
        db.session.commit()
        flash('Job saved successfully.', 'success')

    return redirect(url_for('saved_jobs_view'))

@app.route('/saved_job')
def saved_jobs_view():
    if 'username' not in session:
        flash('Please log in to view saved jobs.', 'warning')
        return redirect(url_for('signin'))

    # Get the logged-in user's ID
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('signin'))

    # Fetch all saved jobs for the user
    saved_jobs = SavedJob.query.filter_by(user_id=user.id).all()

    return render_template('saved_job.html', saved_jobs=saved_jobs)

# Remove a saved job using session
@app.route('/remove_saved_job/<int:job_id>', methods=['POST'])
def remove_saved_job_view(job_id):
    if 'username' not in session:
        flash('Please log in to remove saved jobs.', 'warning')
        return redirect(url_for('signin'))

    # Get the logged-in user's ID
    user = User.query.filter_by(username=session['username']).first()
    
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('signin'))

    # Find and delete the saved job
    saved_job = SavedJob.query.filter_by(user_id=user.id, job_id=job_id).first()
    if saved_job:
        db.session.delete(saved_job)
        db.session.commit()
        flash('Job removed from saved list.', 'success')
    else:
        flash('The job is not in your saved list.', 'info')

    return redirect(url_for('saved_jobs_view'))
    
# code for search bar
@app.route('/search', methods=['GET'])
def search_jobs():
    query = request.args.get('query', '')
    if query:
        # Filter jobs based on query
        jobs = Job.query.filter(Job.title.contains(query) | Job.company.contains(query) | Job.location.contains(query)).all()
    else:
        jobs = Job.query.all()  # Fetch all jobs if no query is provided

    return render_template('job_seeker.html', jobs=jobs)


@app.route('/add_education', methods=['GET', 'POST'])
def add_education():
    # Get the logged-in user's ID (replace with session or authentication mechanism)
    user = User.query.filter_by(username=session['username']).first()
    user_id = user.id

    # Check if the user already has an education record
    existing_education = Education.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        # Get form data
        degree = request.form['degree']
        institution = request.form['institution']
        year_of_passing = request.form['year_of_passing']
        tenth = request.form.get('tenth')
        twelfth = request.form.get('twelfth')

        if existing_education:
            # If education already exists, update the record
            existing_education.degree = degree
            existing_education.institution = institution
            existing_education.year_of_passing = year_of_passing
            existing_education.tenth = tenth
            existing_education.twelfth = twelfth
            
            db.session.commit()
            flash('Education details updated successfully!', 'success')
        else:
            # If no education record exists, create a new one
            new_education = Education(
                user_id=user_id,
                degree=degree,
                institution=institution,
                year_of_passing=year_of_passing,
                tenth=tenth,
                twelfth=twelfth
            )
            try:
                db.session.add(new_education)
                db.session.commit()
                flash('Education details added successfully!', 'success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'An error occurred: {str(e)}', 'danger')

        return redirect(url_for('profile'))  # Redirect to profile page

    # Render the form to add or edit education details
    return render_template('add_education.html', existing_education=existing_education)

@app.route('/edit_education/<int:user_id>', methods=['GET', 'POST'])
def edit_education(user_id):
    user = User.query.get_or_404(user_id)

    # Fetch the user's existing education details
    existing_education = Education.query.filter_by(user_id=user_id).first()
    user_id=user.id

    if request.method == 'POST':
        # Retrieve form data
        degree = request.form.get('degree')
        institution = request.form.get('institution')
        year_of_passing = request.form.get('year_of_passing')

        # If education doesn't exist, create a new entry
        if not existing_education:
            existing_education = Education(user_id=user_id)

        # Update the education details
        existing_education.degree = degree
        existing_education.institution = institution
        existing_education.year_of_passing = year_of_passing

        # Save to the database
        db.session.add(existing_education)
        db.session.commit()

        flash('Education details updated successfully!', 'success')
        return redirect(url_for('profile', user_id=user_id))

    return render_template('edit_education.html', user=user, existing_education=existing_education)


@app.route('/add_skills', methods=['GET', 'POST'])
def add_skills():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    
    user = User.query.filter_by(username=session['username']).first()
    user_id = user.id

    if request.method == 'POST':
        skill_name = request.form['skill_name']

        # Get the user's existing skills
        existing_skills = skills.query.filter_by(user_id=user_id).first()

        # If user already has skills
        if existing_skills:
            # Split the existing skills into a list
            skills_list = existing_skills.skill_name.split(", ")

            # Check if the skill already exists in the list
            if skill_name not in skills_list:
                skills_list.append(skill_name)  # Add the new skill to the list
                updated_skills = ", ".join(skills_list)  # Join skills with a comma

                existing_skills.skill_name = updated_skills  # Update the skills in the database
                db.session.commit()  # Save the changes to the database
                flash('Skills updated successfully!', 'success')
            else:
                flash('This skill is already added.', 'warning')
        else:
            # If no skills exist, create a new entry
            new_skill = skills(user_id=user_id, skill_name=skill_name)
            try:
                db.session.add(new_skill)
                db.session.commit()
                flash('Skill added successfully!', 'success')
            except Exception as e:
                db.session.rollback()  # Rollback in case of error
                flash(f'An error occurred: {str(e)}', 'danger')

        return redirect(url_for('add_skills'))  # Redirect to the same page to refresh the list

    # Retrieve the skills of the current user
    user_skills = skills.query.filter_by(user_id=user_id).all()

    return render_template('add_skills.html', user_skills=user_skills)

#edit skills
@app.route('/edit_skills/<int:user_id>', methods=['GET', 'POST'])
def edit_skills(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.skills = request.form['skills']
        db.session.commit()
        flash('Skills updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_skills.html', user=user)

@app.route('/delete_skill/<int:skill_id>', methods=['POST'])
def delete_skill(skill_id):
    skill = skills.query.get_or_404(skill_id)
    
    # Delete the skill
    try:
        db.session.delete(skill)
        db.session.commit()
        flash('Skill deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('add_skills'))  # Redirect back to the add_skills page



# Route to add work experience
@app.route('/add_work_experience', methods=['GET', 'POST'])
def add_work_experience():
    if 'username' not in session:
        flash("Please log in to add work experience.", "warning")
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    user_id = user.id

    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        role = request.form.get('role')
        job_title = request.form.get('job_title')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = request.form.get('end_date')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        description = request.form.get('description')

        # Check if the user already has a work experience record
        existing_work_experience = WorkExperience.query.filter_by(user_id=user_id).first()

        if existing_work_experience:
            # Update the existing record
            existing_work_experience.company_name = company_name
            existing_work_experience.role = role
            existing_work_experience.job_title = job_title
            existing_work_experience.start_date = start_date
            existing_work_experience.end_date = end_date
            existing_work_experience.description = description
            flash('Work experience updated successfully!', 'success')
        else:
            # Create a new work experience record
            new_work_experience = WorkExperience(
                user_id=user_id,
                company_name=company_name,
                role=role,
                job_title=job_title,
                start_date=start_date,
                end_date=end_date,
                description=description,
            )
            db.session.add(new_work_experience)
            flash('Work experience added successfully!', 'success')

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('profile'))

    return render_template('add_work_experience.html')


@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        # Check if the POST request has the file part
        file = request.files.get('resume')

        if file and allowed_file(file.filename):
            # Secure the file name
            filename = secure_filename(file.filename)
            # Save the file to the upload folder
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Fetch the current user
            user = User.query.filter_by(username=session['username']).first()
            user_id = user.id

            # Check if the user already has a resume
            existing_resume = Resume.query.filter_by(user_id=user_id).first()

            if existing_resume:
                # Delete the old resume file from the server if it exists
                old_resume_path = os.path.join(app.config['UPLOAD_FOLDER'], existing_resume.resume)
                if os.path.exists(old_resume_path):
                    os.remove(old_resume_path)

                # Update the existing resume record
                existing_resume.resume = filename
                flash('Resume updated successfully!', 'success')
            else:
                # If the user doesn't have a resume, create a new record
                new_resume = Resume(user_id=user_id, resume=filename)
                db.session.add(new_resume)
                flash('Resume uploaded successfully!', 'success')

            try:
                # Commit the session to save data to the database
                db.session.commit()
            except Exception as e:
                db.session.rollback()  # Rollback in case of an error
                flash(f"An error occurred: {str(e)}", 'danger')

            return redirect(url_for('upload_resume'))
        else:
            flash('Invalid file type. Please upload a PDF, DOC, DOCX, or TXT file.', 'danger')

    return render_template('upload_resume.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in if not logged in

    # Retrieve the user from the database using the username stored in the session
    user = User.query.filter_by(username=session['username']).first()

    # Check if the user is found
    if user:
        # Fetch the work experience records for the logged-in user
        work_experience = WorkExperience.query.filter_by(user_id=user.id).all()

        # Pass the user and work_experience data to the template
        return render_template('profile.html', user=user, work_experience=work_experience,skills=skills)
    else:
        # If user not found, redirect to sign-in
        return redirect(url_for('signin'))

    
#edit profile
@app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.bio = request.form['bio']
        user.phone_number = request.form.get('phone_number', None)
        user.location = request.form['location']

        # Handle profile picture upload
        profile_picture = request.files.get('profile_picture')
        if profile_picture and profile_picture.filename:
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(file_path)
            user.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to display all candidates
@app.route('/candidates')
def candidates_view():
    try:
        # Fetch user data and filter out recruiters
        users = User.query.filter(User.role != 'recruiter').all()  # Exclude recruiters
        return render_template('candidates.html', users=users)
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('signin'))

    # Check if the user is an admin
    if session.get('role') == 'admin' and session.get('username') == 'admin_username':
        # Fetch admin-specific details or perform admin-specific logic
        admin_details = {
            'username': session['username'],
            'user_id': session.get('user_id', 'N/A'),
            'message': 'Welcome, Admin!'
        }
        return render_template('admin_dashboard.html', admin_details=admin_details)

    # Redirect recruiters to their dashboard
    if session['role'] == 'recruiter':
        return redirect(url_for('admin_dashboard'))

    # Redirect job seekers to their dashboard
    elif session['role'] == 'jobseeker':
        return redirect(url_for('jobseeker_dashboard'))
    
    
    elif session.get('role') == 'superadmin':
        return redirect(url_for('superadmin_dashboard'))

    # Default redirect for any other role
    return redirect(url_for('home'))

    
@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    if 'role' not in session or session['role'] != 'superadmin':
        return redirect(url_for('home'))  # Redirect to home if not superadmin

    # Fetch all users and jobs
    users = User.query.all()
    jobs = Job.query.all()

    return render_template('superadmin_dashboard.html', users=users, jobs=jobs)


# Edit User
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'role' not in session or session['role'] != 'superadmin':
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.role = request.form['role']
        user.bio = request.form.get('bio', user.bio)
        user.profile_picture = request.form.get('profile_picture', user.profile_picture)
        db.session.commit()

        return redirect(url_for('superadmin_dashboard'))

    return render_template('edit_user.html', user=user)


# Edit Job
@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if 'role' not in session or session['role'] != 'superadmin':
        return redirect(url_for('home'))

    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        job.title = request.form['title']
        job.description = request.form['description']
        job.company = request.form['company']
        job.location = request.form['location']
        job.job_type = request.form['job_type']
        job.job_status = request.form['job_status']
        job.salary = request.form.get('salary', job.salary)
        db.session.commit()

        return redirect(url_for('superadmin_dashboard'))

    return render_template('edit_job.html', job=job)


# Delete User
@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'role' not in session or session['role'] != 'superadmin':
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('superadmin_dashboard'))






#khali pasun old code
#manage job (remove)
@app.route('/manage_job')
def manage_job():
    jobs = Job.query.all()  # Fetch all jobs from the database
    return render_template('manage_job.html', jobs=jobs)


# Route to delete a job
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    try:
        # Explicitly delete related job applications before deleting the job
        JobApplication.query.filter_by(job_id=job.id).delete()
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for('manage_job'))


#jobseeker dashboard
@app.route('/jobseeker_dashboard')
def jobseeker_dashboard():
    # Ensure the user is logged in and has the correct role
    if 'username' not in session or session.get('role') != 'jobseeker':
        flash("You must be logged in as a jobseeker to access this page.", "error")
        return redirect(url_for('home'))

    # Fetch all jobs to display in the dashboard
    jobs = Job.query.all()

    # Pass the logged-in username and jobs to the template
    return render_template('job_seeker.html', jobs=jobs, username=session['username'])


# admin route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'recruiter':
        return redirect(url_for('home'))

    # Fetch the user details from the database using the session's username
    user = User.query.filter_by(username=session['username']).first()
    # Fetch jobs for the dashboard
    jobs = Job.query.all()

    # Pass the user object to the template
    return render_template('admin_dashboard.html', user=user, jobs=jobs)


@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if 'username' not in session or session['role'] != 'recruiter':
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        company = request.form['company']
        photo = request.files.get('photo')  # Use request.files.get() to safely handle file input
        location = request.form['location']
        job_type = request.form['job_type']
        job_status = request.form['job_status']
        qualifications = request.form.get('qualifications')
        requirements = request.form.get('requirements')
        responsibilities = request.form.get('responsibilities')
        experience = request.form.get('experience', type=int)
        vacancy = request.form.get('vacancy', type=int)
        salary = request.form.get('salary', type=float)

        # Handle photo if it exists
        if photo and photo.filename:  # Ensure a file is uploaded
            filename = secure_filename(photo.filename)  # Sanitize the file name
            upload_folder = 'static/uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)  # Create folder if it doesn't exist
            photo.save(os.path.join(upload_folder, filename))  # Save the file in the upload folder
        else:
            filename = None  # If no photo is uploaded, set filename to None

        # Fetch the logged-in user
        user = User.query.filter_by(username=session['username']).first()

        # Create and save the new job
        new_job = Job(
            title=title,
            description=description,
            company=company,
            photo=filename,  # Store the filename or None in the database
            location=location,
            job_type=job_type,
            job_status=job_status,
            qualifications=qualifications,
            requirements=requirements,
            responsibilities=responsibilities,
            experience=experience,
            vacancy=vacancy,
            salary=salary,
            recruiter_id=user.id  # Ensure this is included
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('create_job.html')

@app.route('/update_job/<int:job_id>', methods=['GET', 'POST'])
def update_job(job_id):
    if 'username' not in session or session['role'] != 'recruiter':
        return redirect(url_for('home'))

    # Fetch the job to be updated
    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        company = request.form['company']
        photo = request.files.get('photo')  # Handle file upload
        location = request.form['location']
        job_type = request.form['job_type']
        job_status = request.form['job_status']
        qualifications = request.form.get('qualifications')
        requirements = request.form.get('requirements')
        responsibilities = request.form.get('responsibilities')
        experience = request.form.get('experience', type=int)
        vacancy = request.form.get('vacancy', type=int)
        salary = request.form.get('salary', type=float)

        # Update the job with the new data
        job.title = title
        job.description = description
        job.company = company
        job.location = location
        job.job_type = job_type
        job.job_status = job_status
        job.qualifications = qualifications
        job.requirements = requirements
        job.responsibilities = responsibilities
        job.experience = experience
        job.vacancy = vacancy
        job.salary = salary

        # Handle photo upload (if a new photo is uploaded)
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            upload_folder = 'static/uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)  # Create the folder if not exists
            photo.save(os.path.join(upload_folder, filename))  # Save the new photo
            job.photo = filename  # Update the photo field in the job

        # Commit changes to the database
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))  # Redirect to the dashboard

    return render_template('update_job.html', job=job)


# Helper function to check if the user has applied for a specific job
def has_applied_for_job(job_id):
    if 'username' not in session:
        return False  # User is not logged in

    job_seeker_id = session['username']
    user_applied = JobApplication.query.filter_by(job_id=job_id, username=job_seeker_id).all()

    return user_applied is not None

@app.route('/applied_jobs')
def applied_jobs():
    if 'username' not in session:
        flash("Please log in to view your applied jobs.", "warning")
        return redirect(url_for('signin'))

    # Get the logged-in user's username from the session
    username = session['username']

    # Fetch the logged-in user's ID from the User table using username
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('signin'))

    user_id = user.id  # Get the user ID from the User model

    # Query the job applications for the logged-in user using user_id
    job_applications = JobApplication.query.filter_by(user_id=user_id).all()

    # Fetch the corresponding job details for each application
    applied_jobs_details = []
    for application in job_applications:
        applied_jobs_details.append({
            'id': application.job.id,
            'title': application.job.title,
            'company': application.job.company,
            'location': application.job.location,
            'applied_date': application.applied_at.strftime("%d-%m-%Y"),
        })

    # Pass the data to the template
    return render_template('applied_jobs.html', applied_jobs=applied_jobs_details)

@app.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    # Check if the user is logged in
    if 'username' not in session:
        flash("Please log in to apply for the job.", "warning")
        return redirect(url_for('signin'))

    # Get the logged-in user's username from the session
    username = session['username']

    # Fetch the logged-in user's ID from the User table using username
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('signin'))

    user_id = user.id  # Get the user ID from the User model

    # Fetch the job using the job ID
    job = Job.query.get_or_404(job_id)

    # Check if the user has already applied for the job
    existing_application = JobApplication.query.filter_by(job_id=job_id, user_id=user_id).first()
    if existing_application:
        flash("You have already applied for this job.", "info")
        return redirect(url_for('job_details', job_id=job_id))

    # Save the job application with user_id
    try:
        # Create job application
        application = JobApplication(
            job_id=job.id, 
            username=username,  # Store the username
            user_id=user_id,    # Store the user_id fetched from the User table
            applied_at=datetime.now()
        )
        db.session.add(application)
        db.session.commit()

        # Send notification to the recruiter
        notification = Notification(
            job_id=job.id,
            user_id=user_id,
            message=f"{user.username} has applied for your job: {job.title}",
            created_at=datetime.now()
        )
        db.session.add(notification)
        db.session.commit()

        # Send email to recruiter (Assuming 'recruiter' has email stored)
        recruiter = User.query.get(job.user_id)  # Assuming the Job table has recruiter_id field
        msg = Message(
            subject="New Job Application",
            recipients=[recruiter.email],
            body=f"Hello {recruiter.username},\n\n{user.username} has applied for your job '{job.title}'."
        )
        mail.send(msg)

        flash("Your application has been submitted successfully! The recruiter has been notified.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while applying for the job: {e}", "error")
        return redirect(url_for('job_details', job_id=job_id))

    return redirect(url_for('job_details', job_id=job_id))

@app.route('/withdraw_application/<int:job_id>', methods=['POST'])
def withdraw_application(job_id):
    if 'username' not in session:
        flash("Please log in to withdraw your application.", "warning")
        return redirect(url_for('signin'))

    job_seeker_id = session.get('username')  # Get the logged-in user's ID

    # Fetch the job application to be withdrawn
    application = JobApplication.query.filter_by(job_id=job_id, username=job_seeker_id).first()

    if application:
        db.session.delete(application)
        db.session.commit()
        flash("Your application has been withdrawn successfully.", "success")
    else:
        flash("You have not applied for this job.", "info")

    return redirect(url_for('job_details', job_id=job_id))



@app.route('/job_details/<int:job_id>', methods=['GET', 'POST'])
def job_details(job_id):
    if 'username' not in session:
        flash("Please log in to view job details.", "warning")
        return redirect(url_for('signin'))

    # Get the job details using job_id
    job = Job.query.get_or_404(job_id)
    job_seeker_id = session['username']

    # Check if the user has already applied for the job
    user_applied = has_applied_for_job(job_id)

        # If user_applied is empty, it means the user has not applied for the job
    if user_applied:
             # User has already applied for this job
        user_applied = True
    else:
    # User has not applied for this job
        user_applied = False

    if request.method == 'POST':
        if user_applied:  # If already applied, handle withdraw
            # Remove the application from the table
            db.session.delete(user_applied)
            db.session.commit()
            flash("Your application has been withdrawn.", "info")
        else:  # If not applied, handle apply
            # Add the application to the table
            application = JobApplication(job_id=job.id, username=job_seeker_id, applied_at=datetime.now())
            db.session.add(application)
            db.session.commit()
            flash("Your application has been submitted successfully!", "success")

        return redirect(url_for('job_details', job_id=job_id))  # Redirect to reload the page with updated state

    # Render page with the correct button depending on user application status
    return render_template('job_detail.html', job=job, user_applied=user_applied)


@app.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    flash("Notification marked as read.", "success")
    return redirect(url_for('admin_notifications'))

@app.route('/admin_notifications', methods=['GET'])
def admin_notifications():
    # Fetch unread notifications
    notifications = Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()

    return render_template('admin_notifications.html', notifications=notifications)


#about us
@app.route('/about')
def about():
    if 'username' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in if not logged in
    return render_template('about.html')

#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/user_detail/<int:user_id>')
def user_detail_with_id(user_id):
    # Fetch user information from the database
    user = User.query.get_or_404(user_id)  # Fetch user by ID or raise 404 if not found
    work_experience = WorkExperience.query.filter_by(user_id=user_id).all()  # Fetch work experiences for the user
    user_skills = skills.query.filter_by(user_id=user_id).all()  # Fetch skills for the user from a related table
    return render_template('user_detail.html', user=user, work_experience=work_experience, skills=user_skills)

# Route to display user details by ID
@app.route('/user_detail/<int:user_id>')
def user_detail(user_id):
    try:
        user = User.query.get_or_404(user_id)  # Fetch user by ID or return 404 if not found
        return render_template('user_detail.html', user=user)
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('candidates_view'))
    

# Route to render feedback form
@app.route('/feedback', methods=['GET'])
def feedback_form():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    feedback_type = request.form.get('feedback_type')
    message = request.form.get('message')

    # Create a new Feedback instance
    feedback_entry = Feedback(
        name=name,
        email=email,
        feedback_type=feedback_type,
        message=message
    )

    try:
        db.session.add(feedback_entry)
        db.session.commit()
        return redirect(url_for('feedback_form'))  # Redirect to feedback report page
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/applied_candidates/<int:user_id>')
def applied_candidates(user_id):
    try:
        # Define the SQL query with proper parameter binding
        query = text("""
            SELECT 
                ja.id AS application_id, 
                ja.job_id, 
                ja.applied_at,
                ja.user_id, 
                u.username AS user_username,
                u.email AS user_email,
                u.profile_picture AS profile_picture,
                u.phone_number AS user_phone,
                j.title AS job_title,
                j.company AS company_name
            FROM 
                job_application ja
            JOIN 
                `user` u ON ja.user_id = u.id
            LEFT JOIN
                job j ON ja.job_id = j.id
            WHERE 
                ja.user_id = user_id
            ORDER BY 
                ja.applied_at ASC
            LIMIT 25
        """)

        # Execute the query with parameters
        results = db.session.execute(query, {'user_id': user_id})
        
        # Process the results
        applications = [{
            'application_id': row.application_id,
            'job_id': row.job_id,
            'job_title': row.job_title,
            'user_id':row.user_id,
            'company_name': row.company_name,
            'applied_at': row.applied_at,
            'user_username': row.user_username,
            'profile_picture': row.profile_picture,
            'user_email': row.user_email,
            'user_phone': row.user_phone
        } for row in results]

        return render_template(
            'applied_candidates.html',
            applications=applications,
            current_time=datetime.now()
        )

    except Exception as e:
        current_app.logger.error(f"Error fetching applications for user {user_id}: {str(e)}")
        return render_template(
            'applied_candidates.html',
            applications=[],
            error="Unable to fetch applications. Please try again later."
        )
        
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')
  
  
#Reports ALL  
# Route for Job Reports
@app.route('/job_reports', methods=['GET'])
def job_reports():
    # Get query parameters
    title = request.args.get('title')
    company = request.args.get('company')
    location = request.args.get('location')
    job_type = request.args.get('job_type')
    job_status = request.args.get('job_status')
    min_salary = request.args.get('min_salary', type=float)
    max_salary = request.args.get('max_salary', type=float)
    experience = request.args.get('experience', type=int)

    # Build the query
    query = Job.query
    if title:
        query = query.filter(Job.title.ilike(f'%{title}%'))
    if company:
        query = query.filter(Job.company.ilike(f'%{company}%'))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type.ilike(f'%{job_type}%'))
    if job_status:
        query = query.filter(Job.job_status.ilike(f'%{job_status}%'))
    if min_salary:
        query = query.filter(Job.salary >= min_salary)
    if max_salary:
        query = query.filter(Job.salary <= max_salary)
    if experience:
        query = query.filter(Job.experience == experience)

    # Fetch filtered data
    jobs = query.all()

    # Pass jobs to the template
    return render_template('job_reports.html', jobs=jobs)

# Route for User Reports with query parameters
@app.route('/user_reports', methods=['GET', 'POST'])
def user_reports():
    # Get query parameters from the form submission
    username = request.args.get('username')
    email = request.args.get('email')
    role = request.args.get('role')
    location = request.args.get('location')
    phone_number = request.args.get('phone_number')

    # Build the query
    query = User.query
    if username:
        query = query.filter(User.username.ilike(f'%{username}%'))
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))
    if role:
        query = query.filter(User.role.ilike(f'%{role}%'))
    if location:
        query = query.filter(User.location.ilike(f'%{location}%'))
    if phone_number:
        query = query.filter(User.phone_number.ilike(f'%{phone_number}%'))

    # Fetch filtered data
    users = query.all()

    # Pass the data to the template
    return render_template('user_reports.html', users=users)


# Route for main reports page
@app.route('/reports')
def reports():
    return render_template('reports.html')
       
# from sqlalchemy import func
# @app.route('/reports1')
# def reports1():
#     return render_template('reports1.html')

# @app.route('/reports_table')
# def reports_table():
#     return render_template('reports_table.html')

@app.route('/feedback_report')
def feedback_report():
    feedbacks = Feedback.query.all()
    return render_template('feedback_report.html', feedbacks=feedbacks)


@reports_bp.route('/total_jobs_per_company', methods=['GET'])
def total_jobs_per_company():
    start_date = request.args.get('start_date', '2025-01-01')  # Default to earliest date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    
    results = db.session.query(Job.company, db.func.count(JobApplication.id)) \
        .join(JobApplication, Job.id == JobApplication.job_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(Job.company) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()
    
    data = [{"company": r[0], "total_jobs": r[1]} for r in results]
    
    # Extract data for graph
    companies = [item['company'] for item in data]
    job_counts = [item['total_jobs'] for item in data]
    
    return render_template("total_jobs_per_company.html", data=data, start_date=start_date, end_date=end_date, companies=companies, job_counts=job_counts)
#done till here


@reports_bp.route('/total_jobs_per_location', methods=['GET'])
def total_jobs_per_location():
    start_date = request.args.get('start_date', '2025-01-01')  # Default to earliest date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    
    # Query to get job count per location within the date range
    results = db.session.query(Job.location, db.func.count(JobApplication.id)) \
        .join(JobApplication, Job.id == JobApplication.job_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(Job.location) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()

    # Prepare data for the table and graph
    data = [{"location": r[0], "total_jobs": r[1]} for r in results]

    # Check if data is available
    if data:
        locations = [item['location'] for item in data]
        job_counts = [item['total_jobs'] for item in data]
    else:
        locations = []
        job_counts = []

    return render_template("total_jobs_per_location.html", data=data, start_date=start_date, end_date=end_date, locations=locations, job_counts=job_counts)
#done till here


@reports_bp.route('/total_jobs_per_type', methods=['GET'])
def total_jobs_per_type():
    start_date = request.args.get('start_date', '2025-01-01')  # Default to earliest date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    
    # Query to get job count per job type within the date range
    results = db.session.query(Job.job_type, db.func.count(JobApplication.id)) \
        .join(JobApplication, Job.id == JobApplication.job_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(Job.job_type) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()

    # Prepare data for the table and graph
    data = [{"job_type": r[0], "total_jobs": r[1]} for r in results]

    # Check if data is available
    if data:
        job_types = [item['job_type'] for item in data]
        job_counts = [item['total_jobs'] for item in data]
    else:
        job_types = []
        job_counts = []


    return render_template("total_jobs_per_type.html", data=data, start_date=start_date, end_date=end_date, job_types=job_types, job_counts=job_counts)
#done till here


@reports_bp.route('/total_jobs_per_status', methods=['GET'])
def total_jobs_per_status():
    start_date = request.args.get('start_date', '2025-01-01')  # Default to earliest date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))
    
    # Query to get job count per job status within the date range
    results = db.session.query(Job.job_status, db.func.count(JobApplication.id)) \
        .join(JobApplication, Job.id == JobApplication.job_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(Job.job_status) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()

    # Prepare data for the table and graph
    data = [{"job_status": r[0], "total_jobs": r[1]} for r in results]

    # Check if data is available
    if data:
        job_statuses = [item['job_status'] for item in data]
        job_counts = [item['total_jobs'] for item in data]
    else:
        job_statuses = []
        job_counts = []

    return render_template("total_jobs_per_status.html", data=data, start_date=start_date, end_date=end_date, job_statuses=job_statuses, job_counts=job_counts)
#done till here


@reports_bp.route('/total_applications_per_job', methods=['GET'])
def total_applications_per_job():
    start_date = request.args.get('start_date', '2025-01-01')  # Default to earliest date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))

    # Query to get the count of applications per job title
    results = db.session.query(Job.title, db.func.count(JobApplication.id)) \
        .join(JobApplication, Job.id == JobApplication.job_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(Job.title) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()

    # Prepare data for the table and graph
    data = [{"job_title": r[0], "total_applications": r[1]} for r in results]

    # Extract lists for chart rendering
    job_titles = [item['job_title'] for item in data]
    application_counts = [item['total_applications'] for item in data]

    return render_template("total_applications_per_job.html", data=data, start_date=start_date, end_date=end_date, job_titles=job_titles, application_counts=application_counts)
#done till here


@reports_bp.route('/total_applications_per_user', methods=['GET'])
def total_applications_per_user():
    start_date = request.args.get('start_date', '2025-01-01')  # Default start date
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))  # Default end date

    # Query to count applications per user
    results = db.session.query(User.username, db.func.count(JobApplication.id)) \
        .join(JobApplication, User.id == JobApplication.user_id) \
        .filter(JobApplication.applied_at.between(start_date, end_date)) \
        .group_by(User.username) \
        .order_by(db.func.count(JobApplication.id).desc()) \
        .all()

    # Convert query result to list of dictionaries
    data = [{"username": r[0], "total_applications": r[1]} for r in results]

    # Extract usernames and application counts for chart
    usernames = [item['username'] for item in data]
    application_counts = [item['total_applications'] for item in data]

    return render_template("total_applications_per_user.html", data=data, start_date=start_date, end_date=end_date, usernames=usernames, application_counts=application_counts)


 # Route for Total Jobs Posted in a Given Date Range
@reports_bp.route('/total_jobs_posted', methods=['GET'])
def total_jobs_posted():
    # Get date range parameters from request (default: all-time)
    start_date = request.args.get('start_date', '2024-01-01')
    end_date = request.args.get('end_date', datetime.today().strftime('%Y-%m-%d'))

    # Convert string to datetime for query filtering
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD.", 400

    # Debugging: Print date range to console
    print(f"Fetching jobs between {start_date} and {end_date}")
        
    jobs = db.session.query(Job.id, Job.title, Job.company, Job.created_at, User.username) \
    .outerjoin(User, Job.recruiter_id == User.id) \
    .filter(Job.created_at >= start_date, Job.created_at <= end_date) \
    .order_by(Job.created_at.desc()) \
    .all()

    # Debugging: Print fetched jobs
    print(f"Found {len(jobs)} jobs")

    # Convert data to JSON format for rendering
    job_data = [
        {
            "job_id": job[0],
            "job_title": job[1],
            "company_name": job[2],  # Assuming 'company' is a string field in Job
            "recruiter": job[4],  # Fetching recruiter username
            "date_posted": job[3].strftime('%Y-%m-%d')
        }
        for job in jobs
    ]

    return render_template(
        "total_jobs_posted.html",
        jobs=job_data,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

# Register Blueprint with Prefix
app.register_blueprint(reports_bp, url_prefix="/reports")
        
# Ensure database tables are created
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
