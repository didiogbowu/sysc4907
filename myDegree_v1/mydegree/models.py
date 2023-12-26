from mydegree import db

class CourseData(db.Model):
    regst_num = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(15), nullable=False)
    course_title = db.Column(db.String(120), nullable=False)
    semester = db.Column(db.String(15), nullable=False)
    first_day = db.Column(db.Integer, nullable=False)
    second_day = db.Column(db.Integer, nullable=True)
    week_frequency = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"\n{self.course_code}\n{self.course_title}"

