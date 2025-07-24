from init import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields 
from marshmallow.validate import Length, And, Regexp

class Teacher(db.Model):
    # Name of the table
    # __tablename__ = "teachers"

    # Attributes
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(150))

    courses = db.relationship("Course", back_populates="teacher")

class TeacherSchema(SQLAlchemyAutoSchema):
    courses = fields.List(fields.Nested("CourseSchema", exclude=("teacher",)))
    class Meta:
        model = Teacher
        load_instance = True

# Teacher Schema for converting a single entry
teacher_schema = TeacherSchema()

# Teacher Schema for converting multiple entries
teachers_schema = TeacherSchema(many=True)
