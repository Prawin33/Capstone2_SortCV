
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os



app = Flask(__name__)

# Configure session to use filesystem (can be replaced with other session storage)
app.secret_key = 'super-secret-key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

UPLOAD_FOLDER = r'C:\Users\Prave\Downloads\Capstone2\ResumeDB'
ALLOWED_EXTENSIONS = {'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
##Session(app)

# Dummy users for demo purposes
users = {
    'admin': {'password': 'admin', 'role': 'admin'},
    'employer':{'password': '9999', 'role': 'employer'},
    'user': {'password': '1234', 'role': 'user'}
}

# Dummy job search results
dummy_jobs = [
    {'title': 'Software Engineer', 'company': 'ABC Inc.'},
    {'title': 'Data Analyst', 'company': 'XYZ Corp.'},
    {'title': 'Web Developer', 'company': '123 Co.'},
]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        # Store user information in session
        session['username'] = username
        session['role'] = users[username]['role']
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('index'))
    
    
@app.route('/job_search')
def job_search():
    return render_template('job_search.html', jobs=dummy_jobs)

@app.route('/upload_resume')
def upload_resume():
    return render_template('upload_resume.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    
    if 'fileToUpload' not in request.files:
        return 'No file part'
    file = request.files['fileToUpload']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return f'The file {filename} has been uploaded.'
@app.route('/Add_job')
def Add_job():
    return render_template('Add_job.html')
    
@app.route('/post_job', methods=['POST'])
def post_job():
    job_title = request.form['jobTitle']
    job_description = request.form['jobDescription']
    skills = request.form['skills']
    email = request.form['email']
    
    skills_str = ','.join([skill.strip() for skill in skills.split(',')])  # Convert list to string

    
    new_job = Job(title=job_title, description=job_description, skills=skills, email=email)
    db.session.add(new_job)
    db.session.commit()

    return render_template('jobposted.html', job_title=job_title, job_description=job_description, skills=skills_str, email=email)

@app.route('/search_jobs', methods=['GET', 'POST'])
def search_jobs():
    if request.method == 'POST':
        search_query = request.form['searchQuery']
        search_results = Job.query.filter(
            (Job.title.like(f'%{search_query}%')) | 
            (Job.description.like(f'%{search_query}%')) | 
            (Job.skills.like(f'%{search_query}%'))
        ).all()
        for job in search_results:
            job.skills = job.skills.split(',')  # Convert skills string back to a list
        return render_template('search_results.html', jobs=search_results, search_query=search_query)
    return redirect(url_for('welcome'))
    

@app.route('/sortResume')
def sortResume():
    # Read the Excel file
    excel_data_df = pd.read_excel('SortedResumes.xlsx')

    # Convert the dataframe to a dictionary to pass to the template
    data = excel_data_df.to_dict(orient='records')

    return render_template('SorrtResume.html', data=data)

@app.route('/viewResume')
def viewResume():
    # Read the Excel file
    excel_data_df = pd.read_excel('resume.xlsx')

    # Convert the dataframe to a dictionary to pass to the template
    resumes = excel_data_df.to_dict(orient='records')

    return render_template('Viewresume.html', resumes=resumes)

@app.route('/welcome')  
def welcome():
    # Check if user is logged in
    if 'username' in session:
        if session['role'] == 'employer':
            ##return render_template('employer.html', username=session['username'], jobs=jobs)
            jobs = Job.query.all()
            for job in jobs:
                job.skills = job.skills.split(',')  # Convert skills string back to a list
            return render_template('welcome_employer.html', username=session['username'], jobs=jobs)
   
        
        elif session['role'] == 'admin':
            return render_template('welcome_admin.html', username=session['username'])
        
        else:
            return render_template('welcome.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Clear session variables
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

