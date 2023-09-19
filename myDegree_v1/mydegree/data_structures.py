import re
from typing import List
from mydegree import app, db
from mydegree.models import CourseData

class Course:
    def __init__(self, crn, code, title, days, week, start_time, end_time):
        if type(crn) is int: 
            self.crn = crn # course registration number (int)
        else:
            raise TypeError("The CRN 'crn' must be an integer")
            
        if type(code) is str: # might make this a reg ex match check
            self.code = code # course code (str)
        else:
            raise TypeError("The course code 'code' must be a string")

        if type(title) is str: 
            self.title = title # course title (str)
        else:
            raise TypeError("The course title 'title' must be a string")        
        
        if ((len(days) == 1) and (1 <= days[0] <= 5)) or ((len(days) == 2) and (1 <= days[0] <= 5) and (1 <= days[1] <= 5)):
            self.days = days # list of one or two integers
        else:
            raise ValueError("Class days in 'day' must be between 1 and 5 inclusive (Monday to Friday), and there can only be one or two class days in a week")

        if (week == 0) or (week == 1) or (week == 2):
            self.week = week # integer 0, 1, or 2 for weekly, odd biweekly, even biweekly
        else:
            raise ValueError("The value of 'week' must be 0, 1, or 2")

        if (end_time - start_time) > 0.0004:
            self.start_time = start_time # float representing a time in 24h format with minutes converted to decimal (0-0.99)
            self.end_time = end_time # float representing a time in 24h format with minutes converted to decimal (0-0.99)
        else:
            raise ValueError("The end time of a class 'end_time' can be before or at the same time as the start time 'start_time'")

    def __repr__(self):
        return self.code

    def same_day(self, other):
        for day in self.days:
            for other_day in other.days:
                if day == other_day:
                    return True
        return False
                
    def seperate_class_times(self, other):
        return ((other.start_time < self.start_time) and (other.end_time < self.start_time)) or ((other.start_time > self.end_time) and (other.end_time > self.end_time))

    def biweekly_seperate(self, other):
        return (self.week != 0) and (other.week != 0) and (self.week != other.week)
    
class Timetable:
    def __init__(self, courses):
        if type(courses) is list:
            self.courses = courses # list of Course objects
        else:
            raise TypeError("The time table's courses 'courses' must be a list")

    def __repr__(self):
        return str(self.courses)

    def __add__(self, other_timetable):
        sum_timetable = Timetable([])
        
        for course in self.courses:
            sum_timetable.add_course(course)
        
        for other_course in other_timetable.courses:
            sum_timetable.add_course(other_course)
    
        return sum_timetable
        
    def add_course(self, new_course):
        if len(self.courses) == 0:
            self.courses.append(new_course)
            return True
            
        add_to_list = False
        
        for course in self.courses:
            if not course.same_day(new_course):
                add_to_list = True
            else:
                if course.seperate_class_times(new_course):
                    add_to_list = True
                else:
                    if course.biweekly_seperate(new_course):
                        add_to_list = True
                    else:
                        add_to_list = False
                        break

        if add_to_list:
            self.courses.append(new_course)
        else:
            print(f'{new_course} can not be added to time table {self}') # at the end '..time table t1' for example where t1 is the variable assigned the Timetable object
            
        return add_to_list
        
        
def db_model_to_data_struct(db_model: 'models.CourseData') -> 'data_structures.Course':
    days_list = []
    first_day = db_model.first_day
    second_day = db_model.second_day

    days_list.append(first_day)

    if second_day is not None:
        days_list.append(second_day)
    
    return Course(
        crn=db_model.regst_num,
        code=db_model.course_code,
        title=db_model.course_title,
        days=days_list,
        week=db_model.week_frequency,
        start_time=db_model.start_time,
        end_time=db_model.end_time
    )

def merge_crses(first: List['data_structures.Timetable'], second: List['data_structures.Timetable']) -> List['data_structures.Timetable']:
    """ This method implements an algorithm

        Parameters
        ----------
        first : list
            A list of Timetable objects
        second : list
            A list of Timetable objects
            
        Returns
        -------
        list
            A list of Timetable objects
    """
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

def recursive_merge(num_of_crses: int, section_combos: List[List['data_structures.Timetable']]) -> List['data_structures.Timetable']:
    if num_of_crses == 0:
        return []
    elif num_of_crses == 1:
        return section_combos[0]
    else:
        return merge_crses(recursive_merge(num_of_crses - 1, section_combos), section_combos[num_of_crses - 1])

def all_timetables(input_courses: List[str]) -> List['data_structures.Timetable']:    
    NUM_OF_CRSES = len(input_courses)
    num_of_reg_crses = NUM_OF_CRSES
    
    all_sections = []
    lecture_sections = []
    lab_sections = []
    
    section_combinations = []
    
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

    for p in range(NUM_OF_CRSES): 
        lecture_section = lecture_sections[p]
        lab_section = lab_sections[p]
        
        if (len(lab_section) != 0) and (lab_section[0].code.split()[2][0] != 'L'):
            lect_and_lab_sections1 = []
            
            for q in range(len(lecture_section)):
                section_letter = lecture_section[q].code.split()[2]
                
                for r in range(len(lab_section)):
                    timetable = Timetable([])
                    timetable.add_course(lecture_section[q])
                
                    if (lab_section[r].code.split()[2][0] == section_letter) and (timetable.add_course(lab_section[r])):
                        lect_and_lab_sections1.append(timetable)
            
            print(lect_and_lab_sections1)
            
            section_combinations.append(lect_and_lab_sections1)  
        
        else:
            lect_and_lab_sections2 = []

            for q in range(len(lecture_section)):
                if len(lab_section) == 0:
                    timetable = Timetable([])
                    timetable.add_course(lecture_section[q])
                    lect_and_lab_sections2.append(timetable)

                else:
                    for r in range(len(lab_section)):    
                        timetable = Timetable([])
                        timetable.add_course(lecture_section[q])

                        if timetable.add_course(lab_section[r]):
                            lect_and_lab_sections2.append(timetable)       

            print(lect_and_lab_sections2)
            
            section_combinations.append(lect_and_lab_sections2)
            
    print(section_combinations) 
    
    return recursive_merge(NUM_OF_CRSES, section_combinations)             
