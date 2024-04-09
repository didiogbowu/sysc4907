from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

PROGRAM_CHOICES = [
    (0, "Computer Systems Engineering"), 
    (1, "Software Engineering"),
    (2, "Communications Engineering"),
    (3, "Biomedical & Electrical Engineering")
]

CATALOG_YEARS = [
    (3, "202330"),
    (3, "202230"), 
    (3, "202130"),
    (2, "202030"),
    (1, "201930"),
    (0, "201830")
]

class SubmitButtonForm(FlaskForm):
    submit = SubmitField('Load Timetables', validators=[DataRequired()])
        
class TextFieldForm(FlaskForm):
    name_of_course = StringField('Name of Course', validators=[DataRequired()])
    submit = SubmitField('Add')
    
class SelectProgramForm(FlaskForm):
    name_of_course = SelectField('Select your engineering program and catalog year', validators=[DataRequired()], choices=PROGRAM_CHOICES, coerce=str, option_widget=None, validate_choice=True)
    catalog_year = SelectField('', validators=[DataRequired()], choices=CATALOG_YEARS, coerce=str, option_widget=None, validate_choice=True)
    submit = SubmitField('Go')
    