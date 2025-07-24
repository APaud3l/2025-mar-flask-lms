from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from init import db
from models.teacher import Teacher, teachers_schema, teacher_schema

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teachers")

# Routes
# GET /teachers/
@teacher_bp.route("/")
def get_teachers():
    # Define the GET statement
    # SELECT * FROM teacher;
    stmt = db.select(Teacher)
    teachers_list = db.session.scalars(stmt) # Python object
    data = teachers_schema.dump(teachers_list) # JavaScript JSON object

    # For understanding Python objects and JSON objects
    # teachers_list_a = list(db.session.scalars(stmt))
    # print([teacher.name for teacher in teachers_list_a])
    # teacher_json = [teacher["name"] for teacher in data]
    # print(teacher_json)
    if data:
        return jsonify(data)
    else:
        return {"message": "No teacher records found."}, 404


# GET /id
@teacher_bp.route("/<int:teacher_id>")
def get_a_teacher(teacher_id):
    # Define a statement
    stmt = db.select(Teacher).where(Teacher.id == teacher_id)
    # Execute it
    teacher = db.session.scalar(stmt)

    if teacher:
        # Serialise it
        data = teacher_schema.dump(teacher)
        # Return the data
        return jsonify(data)
    else:
        return {"message": f"Teacher with id {teacher_id} does not exist."}, 404

# POST /
@teacher_bp.route("/", methods=["POST"])
def create_a_teacher():
    try:
        # GET info from the REQUEST body
        body_data = request.get_json()

        # Create a Teacher Object from Teacher class with body response data
        new_teacher = Teacher(
            name = body_data.get("name"),
            department = body_data.get("department"),
            address = body_data.get("address")
        )

        # Add the new teacher data to the session
        db.session.add(new_teacher)
        
        # Commit the session
        db.session.commit()

        # Return
        return jsonify(teacher_schema.dump(new_teacher)), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": f"Required field {err.orig.diag.column_name} cannot be null."}, 400
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"message": "Department has to be unique"}, 400
        else:
            return {"message": "Unexpected error occured."}, 400

# DELETE /id
@teacher_bp.route("/<int:teacher_id>", methods=["DELETE"])
def delete_teacher(teacher_id):
    # Find the teacher with the teacher_id
    stmt = db.select(Teacher).where(Teacher.id == teacher_id)
    teacher = db.session.scalar(stmt)
    # if exists
    if teacher:
        # delete the teacher entry
        db.session.delete(teacher)
        db.session.commit()

        return {"message": f"Teacher '{teacher.name}' has been removed successfully."}, 200
    # else:
    else:
        # return an acknowledgement message
        return {"message": f"Teacher with id '{teacher_id}' does not exist"}, 404
    
# UPDATE /teachers/id
@teacher_bp.route("/<int:teacher_id>", methods=["PUT", "PATCH"])
def update_teacher(teacher_id):
    # Get the teacher with id
    stmt = db.select(Teacher).where(Teacher.id == teacher_id)
    teacher = db.session.scalar(stmt)
    # if exists
    if teacher:
        # get the data to be updated
        body_data = request.get_json()
        # make changes
        teacher.name = body_data.get("name") or teacher.name
        teacher.department = body_data.get("department") or teacher.department
        teacher.address = body_data.get("address") or teacher.address
        # commit
        db.session.commit()
        # return
        return jsonify(teacher_schema.dump(teacher))
    # else
    else:
        # return with an error message
        return {"message": f"Teacher with id {teacher_id} does not exist."}, 404