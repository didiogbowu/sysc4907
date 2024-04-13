import re
from typing import List
from mydegree import app, db
from mydegree.models import CourseData

class Course:
    """ This class represents a Carleton University course to be scheduled in a timetable.
    
        Attributes
        ----------
        crn : int
            The course registration number
        code : str
            The course code made up of the department code, the course number, and the 
            course section
        title : str
            The title of the course
        days : list
            A list of numbers (1-5) representing the days of the week the course's 
            meetings occur
        week : int
            The week frequency of the course. 0 if every week. 1 for odd biweekly.
            2 for even biweekly.
        start_time : int
            The start time of the course's meetings in minutes
        end_time : int
            The end time of the course's meetings in minutes
            
        Methods
        -------
        __repr__
            This dunder method is implemented
        same_day(other : 'data_structures.Course')
            Returns true if other has any of the same day values as self
        separate_class_times(other : 'data_structures.Course')
            Returns true if the start_time and end_time values of other do
            not intersect with those of self
        biweekly_separate(other : 'data_structures.Course')
            Returns true if the week values of other and self are 1 or 2 respectively
            without loss of generality
    """
    def __init__(self, crn, code, title, days, week, start_time, end_time):
        self.crn = crn
        self.code = code
        self.title = title  
        self.days = days
        self.week = week
        self.start_time = start_time 
        self.end_time = end_time

    def __repr__(self):
        return self.code

    def same_day(self, other):
        if (self.days[0] is None) or (other.days[0] is None):
            return False
        for day in self.days:
            for other_day in other.days:
                if (day == other_day) or (day is None) or (other_day is None):
                    return True
        return False
                
    def separate_class_times(self, other):
        if (self.start_time is None) or (other.start_time is None):
            return True
        return ((other.start_time < self.start_time) and (other.end_time < self.start_time)) or ((other.start_time > self.end_time) and (other.end_time > self.end_time))

    def biweekly_separate(self, other):
        return (self.week != 0) and (other.week != 0) and (self.week != other.week)
    
class Timetable:
    """ This class represents a timetable scheduled with Carleton University courses.
    
        Attributes
        ----------
        courses : list
            A list of Course objects representing the courses on the timetable

        Methods
        -------
        __repr__
            This dunder method is implemented
        __add__
            This dunder method is implemented. It returns a new Timetable object with all
            the courses from the operands that could be added using add_course().
        add_course(new_course : 'data_structures.Course')
            new_course is added to self.courses provided that for all Course objects currently
            in same_day returns false, separate_class_times returns true, and biweekly_separate
            returns true.
        x_add_course(self, new_course: 'data_structures.Course', x_timetable: 'data_structures.Timetable')
            This does the same thing as add_course() but also considers all the courses (blocked off times) in 
            x_timetable. This method of implementing time filters should be deprecated. See final report 
            Chapter 6.
    """
    def __init__(self, courses: List['data_structures.Course']):
        self.courses = courses

    def __repr__(self) -> str:
        return str(self.courses)

    def __add__(self, other_timetable: 'data_structures.Timetable') -> 'data_structures.Timetable':
        sum_timetable = Timetable([])
        
        for course in self.courses:
            sum_timetable.add_course(course)
        
        for other_course in other_timetable.courses:
            sum_timetable.add_course(other_course)
    
        return sum_timetable
        
    def add_course(self, new_course: 'data_structures.Course') -> bool:
        if len(self.courses) == 0:
            self.courses.append(new_course)
            return True
            
        add_to_list = False
        
        for course in self.courses:
            if not course.same_day(new_course):
                add_to_list = True
            else:
                if course.separate_class_times(new_course):
                    add_to_list = True
                else:
                    if course.biweekly_separate(new_course):
                        add_to_list = True
                    else:
                        add_to_list = False
                        break

        if add_to_list:
            self.courses.append(new_course)
        else:
            print(f'{new_course} can not be added to time table {self}') # at the end '..time table t1' for example where t1 is the variable assigned the Timetable object
            
        return add_to_list
        
    def x_add_course(self, new_course: 'data_structures.Course', x_timetable: 'data_structures.Timetable') -> bool:
        if len(self.courses) == 0:
            self.courses.append(new_course)
            return True
            
        add_to_list = False
        
        for course in self.courses:
            if not course.same_day(new_course):
                add_to_list = True
            else:
                if course.separate_class_times(new_course):
                    add_to_list = True
                else:
                    if course.biweekly_separate(new_course):
                        add_to_list = True
                    else:
                        add_to_list = False
                        break
        
        for course in x_timetable.courses:
            if not course.same_day(new_course):
                add_to_list = True
            else:
                if course.separate_class_times(new_course):
                    add_to_list = True
                else:
                    add_to_list = False
                    break
                        
        if add_to_list:
            self.courses.append(new_course)
        else:
            print(f'{new_course} can not be added to time table {self}') # at the end '..time table t1' for example where t1 is the variable assigned the Timetable object
            
        return add_to_list
        

def get_sections(course_name: str, semester: str) -> List[str]:
    """ This method returns a list of course sections for a course in a given semester.
    
        Parameters
        ----------
        course_name : str
            The department code and the course number
        semester : str
            The semester
            
        Returns
        -------
        List[str]
            The course sections found
    """
    section_letters = []
    SECTION_LETTER = 2
    
    with app.app_context():
        all_sections = CourseData.query.filter(CourseData.course_code.op('regexp')(r'' + course_name), CourseData.semester == semester).all()
        
    for course_data_obj in all_sections:
        section_letters.append(course_data_obj.course_code.split()[SECTION_LETTER])
        
    return section_letters
        
def db_model_to_data_struct(db_model: 'models.CourseData') -> 'data_structures.Course':
    """ This method converts a CourseData object to a Course object. In data_structures.all_timetables,
        the records in the database are retrieved as CourseData objects. These have to be turned into
        Course objects using this method.
    
        Parameters
        ----------
        db_model : models.CourseData
            A CourseData object
            
        Returns
        -------
        data_structures.Course
            A Course object
    """
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
    """ This method implements an algorithm to combine two lists of timetable objects into one. This method is recursively called
        by recursive_merge().

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
    """ This method implements an algorithm to recursively combine all the lists of timetables in the the given list to one list
        of all possible timetables. It is a helper method for all_timetables().

        Parameters
        ----------
        num_of_crses : int
            The number of course names
        section_combos : list
            A two-dimensional list of Timetable objects
            
        Returns
        -------
        list
            A list of all possible Timetable objects containing all course names
    """
    if num_of_crses == 0:
        return []
    elif num_of_crses == 1:
        return section_combos[0]
    else:
        return merge_crses(recursive_merge(num_of_crses - 1, section_combos), section_combos[num_of_crses - 1])

def all_timetables(input_courses: List[str], x_timetable: 'data_structures.Timetable', section_regex: dict, semester: str) -> List['data_structures.Timetable']:   
    """ This method takes in a list of course names and the current semester. Using data from the database it generates a list of all possible 
        Timetable objects containing all course names. The parameter x_timetable is for time filteration. The parameter section_regex is for
        course section filteration.

        Parameters
        ----------
        input_courses : list
            The course names with only the department code and the course number
        x_timetable : 'data_structures.Timetable'
            A Timetable object with blocked off times represented by Course objects
        section_regex : dict
            A dictionary with the course names as the keys and regular expressions 
            representing the course sections to include as the corresponding values
        semester : str
            The given semester (Fall, Winter, or Summer)
            
        Returns
        -------
        list
            A list of all possible Timetable objects containing all course names
    """
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
            all_sections[i] = CourseData.query.filter(CourseData.course_code.op('regexp')(r'' + input_courses[i] + section_regex[input_courses[i]]), 
                CourseData.semester == semester).all()
            
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
                    timetable.x_add_course(lecture_section[q], x_timetable)
                
                    if (lab_section[r].code.split()[2][0] == section_letter) and (timetable.x_add_course(lab_section[r], x_timetable)):
                        lect_and_lab_sections1.append(timetable)
            
            print(lect_and_lab_sections1)
            
            section_combinations.append(lect_and_lab_sections1)  
        
        else:
            lect_and_lab_sections2 = []
            
            for q in range(len(lecture_section)):
                if len(lab_section) == 0:
                    timetable = Timetable([])
                    timetable.x_add_course(lecture_section[q], x_timetable)
                    lect_and_lab_sections2.append(timetable)

                else:
                    for r in range(len(lab_section)):                          
                        timetable = Timetable([])    
                        timetable.x_add_course(lecture_section[q], x_timetable)

                        if timetable.x_add_course(lab_section[r], x_timetable):
                            lect_and_lab_sections2.append(timetable)       

            print(lect_and_lab_sections2)
            
            section_combinations.append(lect_and_lab_sections2)
            
    print(section_combinations) 
    
    return recursive_merge(NUM_OF_CRSES, section_combinations)             
