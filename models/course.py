from init import db

class Course(db.Model):
	__tablename__ = "courses"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False, unique=True)
	duration = db.Column(db.Float)

	# one-to-many with teacher
	teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))

	teacher = db.relationship("Teacher", back_populates="courses")
	enrolments = db.relationship("Enrolment", back_populates="course", cascade="all, delete")
