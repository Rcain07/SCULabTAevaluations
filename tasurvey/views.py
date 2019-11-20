from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from . import app
# from tasurvey.forms import SurveyForm
from tasurvey.models import *
from werkzeug.utils import secure_filename
import os
import xlrd
import secrets as sec
import json

# @app.route("/", methods=['GET', 'POST'])
# @app.route("/survey/", methods=['GET', 'POST'])
@app.route("/survey/<token>", methods=['GET', 'POST'])
def survey(token):
    # surveyFormObject = SurveyForm()
    s = Survey.query.filter_by(token=token).one_or_none()
    if (not s or s.is_done):
        return redirect(url_for('404'))
    if request.method == 'POST':
        s.answers = json.dumps(request.form)
        s.is_done = True
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('success'))
    else:
        return render_template(
            "home.html",
            # form=surveyFormObject,
        )

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

basedir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file/', methods=['GET', 'POST'])
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    path = os.path.join(basedir, UPLOAD_FOLDER, filename)
    classes,surveys = list_classes(path)
    for c in classes:
        db.session.add(Class(number=c[0],name=c[1],size=c[2],instructorEmail=""))
    for s in surveys:
        u = db.session.query(User).filter_by(scuid = s[1]).first() 
        if u == None:
            u = User(email = s[2],scuid = s[1])
            db.session.add(u)
        sur = Survey(token=sec.token_urlsafe(10),user = u)
        u.surveys.append(sur)
        c = db.session.query(Class).filter_by(number=s[0]).first()
        c.instructorEmail = s[3]
        c.surveys.append(sur)
        db.session.add(sur)
    db.session.commit()
    
    return render_template(
        "classes.html",classes=classes
    )

def list_classes(loc):
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(1)

    classes = []
    i = 4
    while i < sheet.nrows-1:
        name = sheet.row_values(i)[1] + ' ' + sheet.row_values(i)[2] + ' ' + sheet.row_values(i)[3]
        # [class number, class name, class size]
        classes.append([sheet.row_values(i)[0], name, sheet.row_values(i)[6]])
        i += 1

    surveys = []
    sheet = wb.sheet_by_index(0)
    i = 2
    while i < sheet.nrows:
        # [class number, student ID, student email, instructor email]
        surveys.append([sheet.row_values(i)[1], sheet.row_values(i)[8], sheet.row_values(i)[9], sheet.row_values(i)[7]])
        i += 1

    return classes,surveys

# REST API for logic apps to send emails
# TO DO: add security
# TO DO: add better error handling

# get information to send emails to students
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
                surveys.append("<li><a href = 'http://rcain07.pythonanywhere.com/"+str(s.token)+"'>"+str(lab.number)+": "+str(lab.name)+"</a></li>")
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

# get evaluation responses to send to corresponding instructors
@app.route('/getResponses', methods=['GET'])
def getResponses():
    resp = {
        "labs":[]
    }
    if Class.query.all() and Survey.query.all():
        classes = db.session.query(Class).all()
        for c in classes:
            print(c.surveys)
            for s in c.surveys:
                print(s.answers)
            email = {
                "name":c.name,
                "number":c.number,
                "size":c.size,
                "instructorEmail":c.instructorEmail,
                "responses":fakeResponses()
            }
            resp["labs"].append(email)
    else:
        resp = {
            "labs":"No classes found"
        }
    return json.dumps(resp)

# calculate scores from evaluations
def formatResponses(responses, lab_size):
    if surveys == []:
        return "No one filled out the evaluation for this lab."
    else:
        #for response in responses:
        return ""

def fakeResponses():
    return {
        "The labs helped me understand the lecture material.":{
            "avg":2.5,
            "std":3
        }
    }
