import pandas as pd
from mydegree import app, db
from mydegree.models import CourseData

# df DataFrame
# number of rows: len(df)
# number of columns: len(df.columns)
# number of elements: df.size

data = pd.read_excel('winter_schedule.xlsx')
column_headers = list(data.columns)

TERM = column_headers[2]
CRN = column_headers[3]
SUBJ = column_headers[4]
CRSE = column_headers[5]
SEQ = column_headers[6]
CATALOG_TITLE = column_headers[7]
DAYS = column_headers[18]
START_TIME =  column_headers[19]
END_TIME = column_headers[20]

char_to_day_num = {
    'M' : 1,
    'T' : 2,
    'W' : 3,
    'R' : 4,
    'F' : 5,
    'S' : 0 # Check module for possible throws
}

biweekly_str_to_num = {'O' : 1, 'E' : 2}

department_codes = [
                      'AERO', 'ACSE', 'ARCC', 'ARCH', 'BIOC', 'BIOM'
                      'BIOL', 'CCDP', 'CDNS', 'CHEM', 'CIVE', 'COMP',
                      'ECOR', 'ELEC', 'ENVE', 'ERTH ', 'MAAE', 'MATH',
                      'MECH', 'PHYS', 'SREE', 'SYSC'
                  ]

bad_apples = []


for i in range(len(department_codes)):
    rows_of_courses = data[data[SUBJ] == department_codes[i]]

    for j in range(len(rows_of_courses)):     
        row = rows_of_courses.iloc[j]

        term = str(int(row[TERM]))
        crn = int(row[CRN])
        dept_code = str(row[SUBJ])
        crse_num = str(row[CRSE])
        crse_section = str(row[SEQ])
        crse_title = str(row[CATALOG_TITLE]) 
        days = str(row[DAYS])

        if (term == '202330'):
            semester = "Fall"
        elif (term == '202410'):
            semester = "Winter"
        else:
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue
        
        try:
            start_time = str(int(row[START_TIME]))
        except ValueError:
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue

        try:
            end_time = str(int(row[END_TIME]))
        except ValueError:
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue

        if (days == 'nan') or (start_time == 'nan') or (end_time == 'nan'):
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue


        day_nums_data = []

        for k in range(len(days)):
            day_nums_data.append(char_to_day_num[days[k]])

        if len(day_nums_data) == 1:
            day_nums_data.append(None)

        if (len(crse_section) == 3) and ((crse_section[2] == 'O') or (crse_section[2] == 'E')):
            week = biweekly_str_to_num[crse_section[2]] # odd biweekly or even biweekly
        else:
            week = 0 # non biweekly

        if len(start_time) == 3:
            s_time = (int(start_time[0]) * 60) + int(start_time[1] + start_time[2])
        elif len(start_time) == 4:
            s_time = (int(start_time[0] + start_time[1]) * 60) + int(start_time[2] + start_time[3])
        else:
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue
        
        if len(end_time) == 3:
            e_time = (int(end_time[0]) * 60) + int(end_time[1] + end_time[2])
        elif len(end_time) == 4:
            e_time = (int(end_time[0] + end_time[1]) * 60) + int(end_time[2] + end_time[3])
        else:
            bad_apples.append(dept_code + ' ' + crse_num + ' ' + crse_section)
            continue
            
        course_data = CourseData(
            regst_num = crn,
            course_code = dept_code + ' ' + crse_num + ' ' + crse_section,
            course_title = crse_title,
            semester = semester,
            first_day = day_nums_data[0],
            second_day = day_nums_data[1],
            week_frequency = week,
            start_time = s_time,
            end_time = e_time
        )

        with app.app_context():
            db.create_all()
            db.session.add(course_data)
            db.session.commit()

print(bad_apples)
