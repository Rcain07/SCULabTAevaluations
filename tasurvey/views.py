from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from . import app
from tasurvey.forms import SurveyForm
from tasurvey.models import *

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
