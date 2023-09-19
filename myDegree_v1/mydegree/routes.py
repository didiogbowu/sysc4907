from flask import render_template, redirect, url_for, request, flash
from mydegree import app
from mydegree.forms import SubmitButtonForm, TextFieldForm
from mydegree.data_structures import all_timetables
from mydegree.render_timetable import course_height, course_mt, course_ml

list_of_names = ['SYSC 3006', 'SYSC 4001', 'ELEC 2607', 'ELEC 2501']

program = "Systems and Computer Engineering"

courses = [
    [{
        'course_code':'ECOR 1042',
        'course_title': 'Data Management'
    },

    {
        'course_code':'MATH 1004',
        'course_title': 'Calculus for Eng. Students'
    },

    {
        'course_code':'CHEM 1101',
        'course_title': 'Chemistry for Eng. Students'
    },

    {
        'course_code':'SYSC 2006',
        'course_title': 'Foundation of Imperative Programming'
    }],

    [{
        'course_code':'MATH 1104',
        'course_title': 'Linear Algebra for Eng. Students'
    },
    
    {
        'course_code':'PHYS 1004',
        'course_title': 'Introductory Electromagnetism & Wave Motion'
    },

    {
        'course_code':'Elective',
        'course_title': 'Complementary Studies Elective'
    },

    {
        'course_code':'SYSC 2310',
        'course_title': 'Introduction to Digital Systems'
    }],

    [{
        'course_code':'MATH 1005',
        'course_title': 'Differential Equations & Infinite Series for Eng. Students'
    },
    
    {
        'course_code':'PHYS 1007',
        'course_title': 'University Physics I'
    },

    {
        'course_code':'SYSC 2004',
        'course_title': 'O.O. Software Development'
    },
    
    {
        'course_code':'Elective',
        'course_title': 'Basic Science Elective'
    }],

    [{
        'course_code':'CCDP 2100',
        'course_title': 'Communication Skills for Eng. Students'
    },
    
    {
        'course_code':'PHYS 1004',
        'course_title': 'Introductory Electromagnetism & Wave Motion'
    },

    {
        'course_code':'SYSC 2510',
        'course_title': 'Probability, Statistics & Random Processes'
    },

    {
        'course_code':'ECOR 2050',
        'course_title': 'Design & Analysis of Engineering Experiment'
    }],

    [{
        'course_code':'MATH 2004',
        'course_title': 'Multivariable Calculus for Eng. Students'
    },
    
    {
        'course_code':'SYSC 2100',
        'course_title': 'Algorithms & Data Structures'
    },

    {
        'course_code':'SYSC 3600',
        'course_title': 'Systems & Simulation'
    },

    {
        'course_code':'SYSC 3320',
        'course_title': 'Computer Systems Design'
    }],

    [{
        'course_code':'SYSC 3006',
        'course_title': 'Computer Organization'
    },
    
    {
        'course_code':'SYSC 4001',
        'course_title': 'Operating Systems'
    },
    
    {
        'course_code':'ELEC 2501',
        'course_title': 'Circuits & Signals'
    },

    {
        'course_code':'ELEC 2607',
        'course_title': 'Switching Circuits'
    }],

    [{
        'course_code':'MATH 3705',
        'course_title': 'Mathematical Methods'
    },
    
    {
        'course_code':'ECOR 3800',
        'course_title': 'Engineering Economics'
    },

    {
        'course_code':'SYSC 3501',
        'course_title': 'Communication Theory'
    },

    {
        'course_code':'SYSC 2320',
        'course_title': 'Computer Organization & Architecture'
    }],

    [{
        'course_code':'MATH 1800',
        'course_title': 'Introduction to Mathematical Reasoning'
    },
    
    {
        'course_code':'SYSC 4602',
        'course_title': 'Computer Communications'
    },

    {
        'course_code':'Elective',
        'course_title': 'Complementary Studies Elective'
    },

    {
        'course_code':'SYSC 3020',
        'course_title': 'Introduction to Software Engineering'
    }]
]


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
        
@app.route("/home")
def home():
    submit_button = SubmitButtonForm()
    if submit_button.is_submitted():
        #flash(f'{list_of_names}', 'success')
        return redirect(url_for('result'))
    return render_template('home.html', courses = courses, title = program, submit_button = submit_button, str = str)