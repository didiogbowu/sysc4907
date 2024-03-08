import os
from flask import render_template, json, jsonify, redirect, url_for, request, flash, current_app
from mydegree import app
from mydegree.forms import SubmitButtonForm, TextFieldForm, SelectProgramForm, PROGRAM_CHOICES
from mydegree.data_structures import Course, Timetable, get_sections, all_timetables
from mydegree.render_timetable import course_height, course_mt, course_ml

list_of_names = []
semester = ""
in_order_load = False

bsc_electives = []
cmplmntry_electives = []
start_year = ""
mainline = []
program = ""
elctv_data = []

x_timetable = Timetable([])

courses = dict()
section_regex = dict()

programs = ["Computer Systems Engineering", "Software Engineering", "Communications Engineering", "Biomedical & Electrical Engineering"]
years = ["2018", "2019", "2020"]

elctv_titles = {
    "BASICSCI": "Basic Science Elective",
    "COMPLSTD": "Complementary Studies Elective",
    "SCIELCTV": "Science Elective",
    "BIOELCTV": "Biomedical Engineering Elective",
    "ENGELCTV": "Engineering Elective"
}

all_elctv_data = [
        [
            {
                "total_num_needed": 3,
                "req_data": [
                    {
                        "type": "specific",
                        "code": "MECH 4503",
                        "max_needed": 1
                    },
                    {
                        "type": "general",
                        "code": "(SYSC|ELEC) (3|4)(\\d{3})",
                        "max_needed": 3
                    },
                    {
                        "type": "general",
                        "code": "SYSC 5(\\d{3})",
                        "max_needed": 2
                    }
                ]
            }
        ],
        [    
            {
                "total_num_needed": 2,
                "req_data": [
                    {
                        "type": "general",
                        "code": "(SYSC|ELEC) (3|4)(\\d{3})",
                        "max_needed": 2
                    }
                ]
            },
        ],
        [
            {
                "total_num_needed": 2,
                "req_data": [
                    {
                        "type": "list",
                        "code": "computerScience",
                        "max_needed": 2
                    },
                    {
                        "type": "general",
                        "code": "SYSC 5(\\d{3})",
                        "max_needed": 2
                    }
                ]
            },
            {
                "total_num_needed": 1,
                "req_data": [
                    {
                        "type": "list",
                        "code": "basicScience",
                        "max_needed": 1
                    },
                    {
                        "type": "specific",
                        "code": "ELEC 2507, ELEC 4705",
                        "max_needed": 1
                    }
                ]
            },
            {
                "total_num_needed": 2,
                "req_data": [
                    {
                        "type": "general",
                        "code": "((SYSC|ELEC) (3|4)(\\d{3})|SYSC 5(\\d{3}))",
                        "max_needed": 2
                    }
                ]
            }
        ],
        [
            {
                "total_num_needed": 1,
                "req_data": [
                    {
                        "type": "specific",
                        "code": "ELEC 3908, SYSC 2004",
                        "max_needed": 1
                    }
                ]
            },
            {
                "total_num_needed": 2,
                "req_data": [
                    {
                        "type": "specific",
                        "code": "ELEC 4709, SYSC 4202, SYSC 4205",
                        "max_needed": 2
                    },
                    {
                        "type": "general",
                        "code": "BIOM 5(\\d{3})",
                        "max_needed": 2
                    }
                ]
            },
            {
                "total_num_needed": 1,
                "req_data": [
                    {
                        "type": "general",
                        "code": "((SYSC|ELEC) (3|4)(\\d{3})|BIOM 5(\\d{3}))",
                        "max_needed": 1
                    }
                ]
            }
        ]
    ]

def resolution(course_code):
    if len(course_code.split(" ")) == 1:
        return ["Elective", elctv_titles[course_code]]
    else:
        return [course_code, courses[course_code]["course_title"]]


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
        global mainline
        global elctv_data
        global programs
        global start_year
        global in_order_load
        
        in_order_load = True
        
        program = programs[int(select_form.name_of_course.data)]
        
        elctv_data = all_elctv_data[int(select_form.name_of_course.data)]
        start_year = years[int(select_form.catalog_year.data)]
        
        with app.app_context():
            file = os.path.join(current_app.static_folder, 'data', 'mainline_courses.json')

            with open(file) as f:
                mainline = json.load(f)[int(select_form.catalog_year.data)][int(select_form.name_of_course.data)]

        return redirect(url_for('home')) # f"<h1>{list(courses.keys())}</h1>" 
    
    return render_template('select_program.html', select_form = select_form)
    
    
@app.route("/home/")
def home():
    global courses
    
    with app.app_context():
        file = os.path.join(current_app.static_folder, 'data', 'eng_electives.json')

        with open(file) as f:
            courses = json.load(f)
    
    return render_template(
        'home.html', 
        len = len,
        range = range,
        str = str,
        list = list,
        in_order_load = in_order_load,
        start_year = start_year,
        mainline = mainline,
        keys = list(courses.keys()),
        courses = courses, 
        title = program,
        elctv_titles = elctv_titles,
        elctv_data = elctv_data,
        resolution = resolution
    )
    
@app.route("/handle_input/", methods=['POST', 'GET']) 
def handle_input():
    received = request.args.get('term_data')
    data = json.loads(received)

    global list_of_names
    global semester
    global section_regex
    
    course_codes = data['course_codes']
    semester = data['semester']
    
    for i in range(len(course_codes)):
        list_of_names.append(course_codes[i])
        section_regex[course_codes[i]] = ""

    url = url_for('filters')
    return jsonify(dict(url = url))

@app.route("/handle_filters/", methods=['POST', 'GET']) 
def handle_filters():
    received = request.args.get('sent')
    data = json.loads(received)
    url = url_for('filters')

    global list_of_names
    global x_timetable
    global section_regex
    
    for j in range(len(data['list_of_names'])):
        list_of_names.append(data['list_of_names'][j])

    section_regex = data['includeSections']
    
    print(section_regex)
    
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
    global x_timetable
    global section_regex
    global data
    
    names_and_sections = dict()
    copy_list = []
    
    for i in range(len(list_of_names)):
        copy_list.append(list_of_names[i])
        course_name = list_of_names[i]
        names_and_sections[course_name] = get_sections(course_name, semester)
    
    x_timetable = Timetable([])
    
    timetables = all_timetables(list_of_names, x_timetable, section_regex, semester) 

    list_of_names.clear()
    semester = ""
 
    if len(timetables) == 0:
        return f"<h1>Unable to generate time table for {copy_list} with the given filter parameters</h1>"
    else:    
        return render_template(
            'result_filters.html',
            len = len,
            range = range,
            str = str,
            course_height = course_height,
            course_mt = course_mt,
            course_ml = course_ml,
            list_of_names = copy_list,
            names_and_sections = names_and_sections,
            timetables = timetables       
        )

@app.route("/result/")
def result():
    global list_of_names
    global semester
    global x_timetable
    global section_regex
    
    timetables = all_timetables(list_of_names, x_timetable, section_regex, semester) 
    
    copy_list = ', '.join(list_of_names)
    
    list_of_names.clear()
    semester = ""
    x_timetable = Timetable([])
 
    if len(timetables) == 0:
        return f"<h1>Unable to generate time table for {copy_list} with the given filter parameters</h1>"
    else:
        
    
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
 