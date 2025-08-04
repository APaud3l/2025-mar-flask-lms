from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes

from init import db
from models.course import Course
from schemas.schemas import course_schema, courses_schema

course_bp = Blueprint("course", __name__, url_prefix="/courses")

# Routes
# GET /courses/
@course_bp.route("/")
def get_courses():
    # Define the GET statement
    # SELECT * FROM course;
    stmt = db.select(Course)
    courses_list = db.session.scalars(stmt) # Python object
    data = courses_schema.dump(courses_list) # JavaScript JSON object

    # For understanding Python objects and JSON objects
    # courses_list_a = list(db.session.scalars(stmt))
    # print([course.name for course in courses_list_a])
    # course_json = [course["name"] for course in data]
    # print(course_json)
    if data:
        return jsonify(data)
    else:
        return {"message": "No course records found."}, 404


# GET /id
@course_bp.route("/<int:course_id>")
def get_a_course(course_id):
    # Define a statement
    stmt = db.select(Course).where(Course.id == course_id)
    # Execute it
    course = db.session.scalar(stmt)

    if course:
        # Serialise it
        data = course_schema.dump(course)
        # Return the data
        return jsonify(data)
    else:
        return {"message": f"Course with id {course_id} does not exist."}, 404

# POST /
@course_bp.route("/", methods=["POST"])
def create_a_course():
    try:
        # GET info from the REQUEST body
        body_data = request.get_json()

        # Create a Course Object from Course class with body response data
        new_course = Course(
            name = body_data.get("name"),
            duration = body_data.get("duration"),
            teacher_id = body_data.get("teacher_id")
        )

        # Add the new course data to the session
        db.session.add(new_course)
        
        # Commit the session
        db.session.commit()

        # Return
        return jsonify(course_schema.dump(new_course)), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": f"Required field {err.orig.diag.column_name} cannot be null."}, 400
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"message": "Course Name has to be unique"}, 400
        else:
            return {"message": "Unexpected error occured."}, 400

# DELETE /id
@course_bp.route("/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    # Find the course with the course_id
    stmt = db.select(Course).where(Course.id == course_id)
    course = db.session.scalar(stmt)
    # if exists
    if course:
        # delete the course entry
        db.session.delete(course)
        db.session.commit()

        return {"message": f"Course '{course.name}' has been removed successfully."}, 200
    # else:
    else:
        # return an acknowledgement message
        return {"message": f"Course with id '{course_id}' does not exist"}, 404
    
# UPDATE /courses/id
@course_bp.route("/<int:course_id>", methods=["PUT", "PATCH"])
def update_course(course_id):
    try:
        # Get the course with id
        stmt = db.select(Course).where(Course.id == course_id)
        course = db.session.scalar(stmt)
        # if exists
        if course:
            # get the data to be updated
            body_data = request.get_json()
            # make changes
            course.name = body_data.get("name") or course.name
            course.duration = body_data.get("duration") or course.duration
            course.teacher_id = body_data.get("teacher_id") or course.teacher_id

            # validate the changes to the course 
            validation_result = course_schema.validate(
                {
                    "name": course.name,
                    "duration": course.duration
                },
                session=db.session
            )
            print(validation_result)
            # if validation_result has truthy value,
            # validation errors have occurred 
            if validation_result:
                return jsonify(validation_result), 400



            # commit
            db.session.commit()
            # return
            return jsonify(course_schema.dump(course))
        # else
        else:
            # return with an error message
            return {"message": f"Course with id {course_id} does not exist."}, 404
    except IntegrityError:
        return {"message": "Name must be unique"}, 400
    except DataError as err:
        return {"message": err.orig.diag.message_primary}, 400