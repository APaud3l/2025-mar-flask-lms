from datetime import date

from init import db


class Enrolment(db.Model):
    __tablename__ = "enrolments"

    id = db.Column(db.Integer, primary_key=True)
    enrolment_date = db.Column(db.Date, default=date.today)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    student = db.relationship("Student", back_populates="enrolments")
    course = db.relationship("Course", back_populates="enrolments")