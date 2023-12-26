import os
from flask import render_template, json, jsonify, redirect, url_for, request, flash, current_app
from mydegree import app
from mydegree.forms import SubmitButtonForm, TextFieldForm, SelectProgramForm, PROGRAM_CHOICES
from mydegree.data_structures import Course, Timetable, get_sections, all_timetables
from mydegree.render_timetable import course_height, course_mt, course_ml

list_of_names = []
semester = ""

courses = []
program = ""

x_timetable = Timetable([])

@app.route("/")
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
    received = request.args.get('term_data')
    data = json.loads(received)

    global list_of_names
    global semester

    course_codes = data['course_codes']
    semester = data['semester']
    
    for i in range(len(course_codes)):
        list_of_names.append(course_codes[i])

    url = url_for('filters')
    return jsonify(dict(url = url))

@app.route("/handle_filters/", methods=['POST', 'GET']) 
def handle_filters():
    received = request.args.get('sent')
    data = json.loads(received)
    url = url_for('result')

    global list_of_names
    global x_timetable
    
    for j in range(len(data['list_of_names'])):
        list_of_names.append(data['list_of_names'][j])
    
    for i in range(len(data['blockedOff'])):
        x_timetable.add_course(
            Course(
                crn=0,
                code="NONE 0000",
                title="Filler Course",
                days=[data['blockedOff'][i]['day']],
                week=0,
                start_time=data['blockedOff'][i]['startTime'],
                end_time=data['blockedOff'][i]['endTime']
            )
        )

    return jsonify(dict(url = url))


@app.route("/filters/")
def filters():
    global list_of_names
    global semester
    
    names_and_sections = dict()
    copy_list = []
    
    for i in range(len(list_of_names)):
        copy_list.append(list_of_names[i])
        course_name = list_of_names[i]
        names_and_sections[course_name] = get_sections(course_name, semester)
    
    list_of_names.clear()
    
    return render_template(
        'filters.html',
        len = len,
        range = range,
        str = str,
        course_height = course_height,
        course_mt = course_mt,
        course_ml = course_ml,
        list_of_names = copy_list,
        names_and_sections = names_and_sections
    )

@app.route("/result/")
def result():
    global list_of_names
    global x_timetable
    global data
    
    timetables = all_timetables(list_of_names, x_timetable, semester) 
    list_of_names.clear()
    x_timetable = Timetable([])
 
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
 