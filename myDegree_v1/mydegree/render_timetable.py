HRS_TO_MINS = 60
TIMETABLE_ST = 8 * HRS_TO_MINS

COURSE_WIDTH = 100
HEIGHT = 30
HEIGHT_REF = 30
B_HEIGHT = 70
B_WIDTH = 50

def course_height(end_time, start_time):
    return (HEIGHT * ((end_time - start_time) / HEIGHT_REF))
    
def course_mt(start_time):
    return (HEIGHT * ((start_time - TIMETABLE_ST) / HEIGHT_REF))
    
def course_ml(day):
    return COURSE_WIDTH * (day - 1)