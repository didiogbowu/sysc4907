HRS_TO_MINS = 60 # The number of minutes in one hour
TIMETABLE_ST = 8 * HRS_TO_MINS # This represents 8 o'clock in the morning

COURSE_WIDTH = 100 # The CSS width in px of each time slot
HEIGHT = 30 # The CSS height in px
HEIGHT_REF = 30 # This was used for scaling the height. HEIGHT divided by HEIGHT_REF gives the scale

def course_height(end_time, start_time):
    return (HEIGHT * ((end_time - start_time) / HEIGHT_REF))
    
def course_mt(start_time):
    return (HEIGHT * ((start_time - TIMETABLE_ST) / HEIGHT_REF))
    
def course_ml(day):
    return COURSE_WIDTH * (day - 1)