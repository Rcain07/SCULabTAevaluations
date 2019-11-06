from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class SurveyForm(FlaskForm):
    Answers = StringField('Answers', validators=[DataRequired()])
    submit = SubmitField('Submit')

    