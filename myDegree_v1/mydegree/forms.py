from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SubmitButtonForm(FlaskForm):
    submit = SubmitField('Submit', validators=[DataRequired()])
        
class TextFieldForm(FlaskForm):
    name_of_course = StringField('Name of Course', validators=[DataRequired()])
    submit = SubmitField('Add')