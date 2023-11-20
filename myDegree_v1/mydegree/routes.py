import os
from flask import render_template, json, jsonify, redirect, url_for, request, flash, current_app
from mydegree import app
from mydegree.forms import SubmitButtonForm, TextFieldForm, SelectProgramForm, PROGRAM_CHOICES
from mydegree.data_structures import all_timetables
from mydegree.render_timetable import course_height, course_mt, course_ml

list_of_names = []
semester = ""

courses = []
program = ""

@app.route("/")
@app.route("/select_program/", methods=['GET', 'POST'])
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
    
    return render_template('select_program.html', select_form = select_form)
    
    
@app.route("/home/")
def home():
    return render_template(
        'home.html', 
        len = len,
        range = range,
        str = str,
        courses = courses, 
        title = program
    )
    
@app.route("/handle_input/", methods=['POST', 'GET']) 
def handle_input():
    recieved = request.args.get('term_data')
    data = json.loads(recieved)

    global list_of_names
    global semester

    course_codes = data['course_codes']
    semester = data['semester']
    
    for i in range(len(course_codes)):
        list_of_names.append(course_codes[i])

    url = url_for('filters')
    return jsonify(dict(url = url))

@app.route("/filters/")
def filters():
    global list_of_names
    
    return render_template(
        'filters.html',
        len = len,
        range = range,
        str = str,
        course_height = course_height,
        course_mt = course_mt,
        course_ml = course_ml,
        list_of_names = list_of_names
    )

@app.route("/result/")
def result():
    timetables = all_timetables(list_of_names, semester) 
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
 
@app.route("/input_page/", methods=['GET', 'POST'])
def input_page():
    text_field = TextFieldForm()
    submit_button = SubmitButtonForm()
    
    if text_field.validate_on_submit():
        list_of_names.append(text_field.name_of_course.data)
        flash(f'{list_of_names}', 'success')
        return redirect(url_for('input_page'))
        
    if submit_button.is_submitted():
        return redirect(url_for('result'))
    return render_template('input_courses.html', text_field = text_field, submit_button = submit_button) 
