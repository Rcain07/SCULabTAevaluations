'''
Description: A file with functions that serve as endpoints 
for our backend API to interact with our frontend and our logic apps.
'''

from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from . import app,login
# from tasurvey.forms import SurveyForm
from tasurvey.models import *
from werkzeug.utils import secure_filename
import os
import xlrd
import secrets as sec
import json
from statistics import stdev, mean
from flask_login import current_user, login_user
from tasurvey.forms import LoginForm
from flask_login import logout_user
from flask_login import login_required

# Endpoint for catch-all
# input: none
# output: rendered 404 error HTML template
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("404.html")

# Endpoint for end
# input: none
# output: rendered HTML template
@app.route("/end", methods=['GET', 'POST'])
def end():
    return render_template("end.html")

# Survey Logic, used for finding the unique survey, filling it out and saving it in the database
# input: token (string)
# output: rendered HTML template
@app.route("/survey/<token>", methods=['GET', 'POST'])
def survey(token):
    s = Survey.query.filter_by(token=token).one_or_none()
    if (not s or s.is_done):
        return redirect(url_for('home'))
    if request.method == 'POST':
        s.answers = json.dumps(request.form)
        s.is_done = True
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('end'))
    else:
        return render_template(
            "home.html",
            # form=surveyFormObject,
        )

# Endpoint to a succesful survey submission
# input: none
# output: rendered template with responses from that survey
@app.route("/success", methods=['GET', 'POST'])
def success():
    # get survey response from database
    responses = []
    if Survey.query.all():
        data = db.session.query(Survey).all()
        for response in data:
            responses.append([response.id, response.token, response.answers])
    else:
        responses = ['No surveys in the database']
    return  render_template(
        "success.html",responses=responses
        
    )

# global variables for allowed file types
basedir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Determines file type is allowed
# input: filename
# output: true if file type is allowed 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload file
# input: none
# output: rendered template with filename (redirects to uploaded_file(filename))
@app.route('/upload_file/', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(basedir, UPLOAD_FOLDER, filename)
            file.save(path)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template(
        "upload.html",
    )

# Update database with uploaded file information
# input: filename
# output: rendered template with classes information
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # parse file
    path = os.path.join(basedir, UPLOAD_FOLDER, filename)
    classes,surveys = list_classes(path)
    # update classes in database
    for c in classes:
        if db.session.query(Class).filter_by(number=c[0],name=c[1],size=c[2]).one_or_none():
            continue
        db.session.add(Class(number=c[0],name=c[1],size=c[2],instructorEmail=""))
    # update student information in database
    for s in surveys:
        u = User.query.filter_by(scuid = s[1]).one_or_none() or db.session.query(User).filter_by(scuid = s[1]).one_or_none()
        if u == None:
            u = User(email = s[2],scuid = s[1])
            db.session.add(u)
        if s[2] != '':
            u.email = s[2]
        c = db.session.query(Class).filter_by(number=s[0]).one_or_none() or Class.query.filter_by(number=s[0]).one_or_none()
        c.instructorEmail = s[3]
        survlist = c.surveys.filter_by(id=u.id).one_or_none()
        if survlist == None:
            sur = Survey(token=sec.token_urlsafe(10),user = u)
            u.surveys.append(sur)
            c.surveys.append(sur)
            db.session.add(sur)
    db.session.commit()
    
    return render_template(
        "classes.html",classes=classes
    )

# Parse file to get list of classes and students for each
# input: location of file
# output: classes array and surveys array
def list_classes(loc):
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(1)

    classes = []
    i = 4 # skip initial lines with column labels
    while i < sheet.nrows-1:
        name = sheet.row_values(i)[1] + ' ' + sheet.row_values(i)[2] + ' ' + sheet.row_values(i)[3]
        # [class number, class name, class size]
        classes.append([sheet.row_values(i)[0], name, sheet.row_values(i)[6]])
        i += 1

    surveys = []
    sheet = wb.sheet_by_index(0)
    i = 1 # skip first lines with column label
    while i < sheet.nrows:
        # [class number, student ID, student email, instructor email]
        surveys.append([sheet.row_values(i)[1], sheet.row_values(i)[8], sheet.row_values(i)[9], sheet.row_values(i)[7]])
        i += 1
    return classes,surveys

# Endpoint for admin page
# input: none
# output: rendered HTML template
@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    return render_template("admin.html")

# Endpoint for 404 error
# input: none
# output: rendered HTML template
@app.route("/404", methods=['GET', 'POST'])
def error():
    return render_template("404.html")

# Loads user
# input: user ID
# output: user ID information from database
@login.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Endpoint for admin login page
# input: none
# output: rendered HTML template with admin form
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('postLogin'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        print(admin)
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(admin, remember=form.remember_me.data)
        return redirect(url_for('postLogin'))
    return render_template('login.html', form=form)

# Endpoint for after admin logs in
# input: none
# output: rendered HTML template
@app.route("/postLogin", methods=['GET', 'POST'])
@login_required
def postLogin():
    return render_template("postLogin.html")

# Endpoint for admin logout
# input: none
# output: rendered HTML template that redirects to login page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
# Get information to send emails to students
# input: none
# output: formatted JSON with list of students and their respective email information
@app.route('/getStudents', methods=['GET'])
def getStudents():
    resp = {
        "students":[]
    }
    if db.session.query(User).all():
        users = db.session.query(User).all()
        for u in users:
            surveys = []
            for s in u.surveys:
                lab = db.session.query(Class).filter_by(id=s.class_id).first()
                surveys.append("<li><a href = 'http://rcain07.pythonanywhere.com/survey/"+str(s.token)+"'>"+str(lab.number)+": "+str(lab.name)+"</a></li>")
            student = {
                "studentEmail":u.email,
                "surveys": surveys
            }
            resp["students"].append(student)
    else:
        resp = {
            "students":"No students found"
        }
    return json.dumps(resp)

# Get evaluation responses to send to corresponding instructors
# input: none
# output: formatted JSON with list of evaluation summaries for each respective professor
@app.route('/getResponses', methods=['GET'])
def getResponses():
    resp = {
        "labs":[]
    }
    if Class.query.all():
        classes = db.session.query(Class).all()
        for c in classes:
            email = {
                "name":c.name,
                "number":str(c.number),
                "instructorEmail":c.instructorEmail,
                "responses":parseResponses(c.surveys, c.size)
            }
            resp["labs"].append(email)
    else:
        resp = {
            "labs":"No classes found"
        }
    return json.dumps(resp)

# Summarize responses for one lab
# input: survey responses in JSON and lab size for one lab
# output: HTML formatted string with summary of responses
def parseResponses(responses_json, lab_size):
    if responses_json:
        responses = []
        responses_list = list(responses_json)
        for i in range(len(responses_list)):
            if responses_list[i].is_done == True:
                responses.append(json.loads(responses_list[i].answers))
        if len(responses) == 0:
            return "<p>No one filled out the evaluation for this lab.</p>"
        formatted = "<p>"+str(len(responses))+" students filled out the survey out of "+str(lab_size)+"</p><br><ul>"
        questions = list(responses[0].keys())
        # parse JSON response
        for i in range(len(questions)):
            if i <= 3:
                a = [int(d[questions[i]]) for d in responses]
                formatted += getSummary(questions[i], a)
            elif i > 3 and i <= 5:
                a = [d[questions[i]] for d in responses]
                formatted += clusterText(questions[i], a)
            elif i > 5 and i <= 10:
                a = [int(d[questions[i]]) for d in responses]
                formatted += getSummary(questions[i], a)
            elif i == 11:
                a = [d[questions[i]] for d in responses]
                formatted += clusterText(questions[i], a)
            elif i > 11 and i <= 14:
                a = [int(d[questions[i]]) for d in responses]
                formatted += getSummary(questions[i], a)
            elif i == 15:
                a = [d[questions[i]] for d in responses]
                formatted += clusterText(questions[i], a)
            elif i > 15 and i <= 18:
                a = [d[questions[i]] for d in responses]
                formatted += getCounts(questions[i], a)
            else:
                a = [d[questions[i]] for d in responses]
                formatted += clusterText(questions[i], a)
        return formatted+"</ul>"
    else:
        return "<p>Error occurred.</p>"

# Get the standard deviation and average value for one question
# input: question (string) and array of values for that question
# output: HTML formatted string with the standard deviation and average value for one question
def getSummary(question, values):
    avg = mean(values)
    if len(values) > 1:
        std = stdev(values)
    else:
        std = 0
    return "<li>"+question+" Average response: "+str(round(avg,2))+" Standard deviation: "+str(round(std,2))+"</li>"

# Get the counts for each answer choice of one question
# input: question (string) and array of values for that question
# output: HTML formatted string with the counts for each answer choice
def getCounts(question, values):
    temp = ""
    counts = {x:values.count(x) for x in values}
    for key, value in counts.items():
        temp += "<li>'"+str(key)+"': "+str(value)+"</li>"
    return "<li>"+question+"</li><ul>"+temp+"</ul>"

# Cluster text for one question
# input: question (string) and array of values for that question
# output: HTML formatted string with a list of text responses
def clusterText(question, values):
    temp = ""
    for p in values:
        if p != "":
            temp += "<li>"+str(p)+"</li>"
    return "<li>"+question+"</li><ul>"+temp+"</ul>"
