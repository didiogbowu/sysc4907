import os
from flask import render_template, json, redirect, url_for, request, flash, current_app
from mydegree import app
from mydegree.forms import SubmitButtonForm, TextFieldForm, SelectProgramForm, PROGRAM_CHOICES
from mydegree.data_structures import all_timetables
from mydegree.render_timetable import course_height, course_mt, course_ml

list_of_names = []
courses = []
program = ""

@app.route("/")
@app.route("/input_page", methods=['GET', 'POST'])
def input_page():
    text_field = TextFieldForm()
    submit_button = SubmitButtonForm()
    
    if text_field.validate_on_submit():
        list_of_names.append(text_field.name_of_course.data)
        flash(f'{list_of_names}', 'success')
        return redirect(url_for('input_page'))
        
    if submit_button.is_submitted():
        #flash(f'{list_of_names}', 'success')
        return redirect(url_for('result'))
    return render_template('input_courses.html', text_field = text_field, submit_button = submit_button)

@app.route("/result")
def result():
    timetables = all_timetables(list_of_names) 
    list_of_names.clear()
    return render_template(
        'result.html',
        len = len,
        range = range,
        str = str,
        course_height = course_height,
        course_mt = course_mt,
        course_ml = course_ml,
        timetables = timetables       
    )
    
@app.route("/select_program", methods=['GET', 'POST'])
def select_program():
    select_form = SelectProgramForm()
    
    if select_form.validate_on_submit():
        global program
        global courses
        
        program = dict(PROGRAM_CHOICES).get(select_form.name_of_course.data)
        
        with app.app_context():
            file = os.path.join(current_app.static_folder, 'data', str(select_form.name_of_course.data) + '.json')

            with open(file) as f:
                courses = json.load(f)
        
        return redirect(url_for('home'))
    
    return render_template('select_program.html', select_form = select_form);
    
    
@app.route("/home")
def home():
    submit_button = SubmitButtonForm()
    if submit_button.is_submitted():
        return redirect(url_for('result'))
    return render_template(
        'home.html', 
        len = len,
        range = range,
        str = str,
        courses = courses, 
        title = program, 
        submit_button = submit_button
    )
    
@app.route("/handle_input", methods=['POST', 'GET']) 
def handle_input():
    if request.method == "POST":
        recieved = request.get_data()
        return redirect(url_for('handle_input'))
        
    return "<h1>Nice</h1>"