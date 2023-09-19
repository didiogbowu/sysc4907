import re
from mydegree import app, db
from mydegree.models import CourseData
from mydegree.data_structures import Course, Timetable

def db_model_to_data_struct(db_model):
    days_list = []
    first_day = db_model.first_day
    second_day = db_model.second_day

    days_list.append(first_day)

    if second_day is not None:
        days_list.append(second_day)
    
    return Course(
        code=db_model.course_code,
        title=db_model.course_title,
        days=days_list,
        week=db_model.week_frequency,
        start_time=db_model.start_time,
        end_time=db_model.end_time
    )

def merge_crses(first, second):
    merger = []
    
    for first_timetable in first:
        for second_timetable in second:
            new_timetable = Timetable([])
            new_timetable = new_timetable + first_timetable

            if len(second_timetable.courses) == 1:
                if not new_timetable.add_course(second_timetable.courses[0]):
                    continue
                merger.append(new_timetable)
            else:
                if (not new_timetable.add_course(second_timetable.courses[0])) or (not new_timetable.add_course(second_timetable.courses[1])):
                    continue
                merger.append(new_timetable)

    return merger

def recursive_merge(num_of_crses, section_combos):
    if num_of_crses == 0:
        return []
    elif num_of_crses == 1:
        return section_combos[0]
    else:
        return merge_crses(recursive_merge(num_of_crses - 1, section_combos), section_combos[num_of_crses - 1])

def all_timetables(input_courses):    
    #input_courses = ['AERO 4003', 'MAAE 3202', 'CCDP 2004']
    NUM_OF_CRSES = len(input_courses)

    all_sections = []
    lecture_sections = []
    lab_sections = []

    for i in range(NUM_OF_CRSES):
        all_sections.append(list())
        lecture_sections.append(list())
        lab_sections.append(list())
        
        with app.app_context():
            all_sections[i] = CourseData.query.filter(CourseData.course_code.op('regexp')(r'' + input_courses[i])).all()
            
            for course_data_obj in all_sections[i]:
                lect_pattern = re.compile(r'' + input_courses[i] + r'\s\w$')
                lab_pattern = re.compile(r'' + input_courses[i] + r'\s(\w{2}|\w{3})$')

                if lect_pattern.fullmatch(course_data_obj.course_code):
                    lecture_sections[i].append(db_model_to_data_struct(course_data_obj))
                elif lab_pattern.fullmatch(course_data_obj.course_code):
                    lab_sections[i].append(db_model_to_data_struct(course_data_obj))
                else:
                    print("Something's not right")

    section_combinations = []

    for p in range(NUM_OF_CRSES):
        lecture_section = lecture_sections[p]
        lab_section = lab_sections[p]

        lect_and_lab_sections = []

        for q in range(len(lecture_section)):
            if len(lab_section) == 0:
                timetable = Timetable([])
                timetable.add_course(lecture_section[q])
                lect_and_lab_sections.append(timetable)

            else:
                for r in range(len(lab_section)):    
                    timetable = Timetable([])
                    timetable.add_course(lecture_section[q])

                    if timetable.add_course(lab_section[r]):
                        lect_and_lab_sections.append(timetable)       

        section_combinations.append(lect_and_lab_sections)


    #two_courses = []
    #three_courses = []

    #two_courses = merge_crses(section_combinations[0], section_combinations[1])
    #three_courses = merge_crses(merge_crses(section_combinations[0], section_combinations[1]), section_combinations[2])
        
    return recursive_merge(NUM_OF_CRSES, section_combinations)









