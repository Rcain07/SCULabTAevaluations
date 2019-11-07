from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from . import app
from tasurvey.forms import SurveyForm
from tasurvey.models import *
from werkzeug.utils import secure_filename
import os
import xlrd

# User(email="rcain@scu.edu")

@app.route("/", methods=['GET', 'POST'])
@app.route("/survey/", methods=['GET', 'POST'])
@app.route("/survey/<token>", methods=['GET', 'POST'])
def survey(token = None):
    surveyFormObject = SurveyForm()
    if surveyFormObject.validate_on_submit():
        surv = Survey(token="test",answers=surveyFormObject.data['Answers'])
        db.session.add(surv)
        db.session.commit()
        return redirect(url_for('success'))
    return render_template(
        "survey.html",
        form=surveyFormObject,
    )

@app.route("/success", methods=['GET', 'POST'])
def success():
    return  render_template(
        "success.html",
        
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
    classes = list_classes(path)
    return render_template(
        "classes.html",classes=classes
    )
  

def list_classes(loc):
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(1)
    sheet.cell_value(0, 0)

    classes = []
    i = 4
    while i < sheet.nrows-1:
        name = sheet.row_values(i)[1] + ' ' + sheet.row_values(i)[2] + ' ' + sheet.row_values(i)[3]
        classes.append([sheet.row_values(i)[0], name, sheet.row_values(i)[6]])
        i += 1

    return classes
