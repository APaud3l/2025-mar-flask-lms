from init import db

class Student(db.Model):
    # Name of the table
    __tablename__ = "students"
    
    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(100))

    enrolments = db.relationship("Enrolment", back_populates="student", cascade="all, delete")