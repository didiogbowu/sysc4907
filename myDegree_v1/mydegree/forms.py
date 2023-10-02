from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

PROGRAM_CHOICES = [
    ("cse", "Systems and Computer Engineering"), 
    ("se", "Software Engineering"),
    ("comm_eng", "Communications Engineering"),
    ("bee", "Biomedical & Electrical Engineering")
]

class SubmitButtonForm(FlaskForm):
    submit = SubmitField('Load Timetables', validators=[DataRequired()])
        
class TextFieldForm(FlaskForm):
    name_of_course = StringField('Name of Course', validators=[DataRequired()])
    submit = SubmitField('Add')
    
class SelectProgramForm(FlaskForm):
    name_of_course = SelectField('Select your engineering program', validators=[DataRequired()], choices=PROGRAM_CHOICES, coerce=str, option_widget=None, validate_choice=True)
    submit = SubmitField('Go')