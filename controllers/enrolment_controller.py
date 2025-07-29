from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from init import db
from models.enrolment import Enrolment
from schemas.schemas import enrolment_schema, enrolments_schema

enrolment_bp = Blueprint("enrolment", __name__, url_prefix="/enrolments")

# Routes
# GET /enrolments/
@enrolment_bp.route("/")
def get_enrolments():
    course_id = request.args.get("course_id", type=int)
    student_id = request.args.get("student_id", type=int)
    # Define the GET statement
    # SELECT * FROM enrolment;
    stmt = db.select(Enrolment)

    if course_id:
        stmt = stmt.where(Enrolment.course_id == course_id)
    if student_id:
        stmt = stmt.where(Enrolment.student_id == student_id)
        
    enrolments_list = db.session.scalars(stmt) # Python object
    data = enrolments_schema.dump(enrolments_list) # JavaScript JSON object

    # For understanding Python objects and JSON objects
    # enrolments_list_a = list(db.session.scalars(stmt))
    # print([enrolment.name for enrolment in enrolments_list_a])
    # enrolment_json = [enrolment["name"] for enrolment in data]
    # print(enrolment_json)
    if data:
        return jsonify(data)
    else:
        return {"message": "No enrolment records found."}, 404


# GET /id
@enrolment_bp.route("/<int:enrolment_id>")
def get_a_enrolment(enrolment_id):
    # Define a statement
    stmt = db.select(Enrolment).where(Enrolment.id == enrolment_id)
    # Execute it
    enrolment = db.session.scalar(stmt)

    if enrolment:
        # Serialise it
        data = enrolment_schema.dump(enrolment)
        # Return the data
        return jsonify(data)
    else:
        return {"message": f"Enrolment with id {enrolment_id} does not exist."}, 404

# POST /
@enrolment_bp.route("/", methods=["POST"])
def create_a_enrolment():
    try:
        # GET info from the REQUEST body
        body_data = request.get_json()

        # Create a Enrolment Object from Enrolment class with body response data
        new_enrolment = Enrolment(
            student_id = body_data.get("student_id"),
            course_id = body_data.get("course_id"),
            enrolment_date = body_data.get("enrolment_date")
        )

        # Add the new enrolment data to the session
        db.session.add(new_enrolment)
        
        # Commit the session
        db.session.commit()

        # Return
        return jsonify(enrolment_schema.dump(new_enrolment)), 201
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": f"Required field {err.orig.diag.column_name} cannot be null."}, 400
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"message": err.orig.diag.message_detail}, 400

# DELETE /id
@enrolment_bp.route("/<int:enrolment_id>", methods=["DELETE"])
def delete_enrolment(enrolment_id):
    # Find the enrolment with the enrolment_id
    stmt = db.select(Enrolment).where(Enrolment.id == enrolment_id)
    enrolment = db.session.scalar(stmt)
    # if exists
    if enrolment:
        # delete the enrolment entry
        db.session.delete(enrolment)
        db.session.commit()

        return {"message": f"Enrolment '{enrolment.name}' has been removed successfully."}, 200
    # else:
    else:
        # return an acknowledgement message
        return {"message": f"Enrolment with id '{enrolment_id}' does not exist"}, 404
    
# UPDATE /enrolments/id
# @enrolment_bp.route("/<int:enrolment_id>", methods=["PUT", "PATCH"])
# def update_enrolment(enrolment_id):
    # Get the enrolment with id
    stmt = db.select(Enrolment).where(Enrolment.id == enrolment_id)
    enrolment = db.session.scalar(stmt)
    # if exists
    if enrolment:
        # get the data to be updated
        body_data = request.get_json()
        # make changes
        enrolment.name = body_data.get("name") or enrolment.name
        enrolment.email = body_data.get("email") or enrolment.email
        enrolment.address = body_data.get("address") or enrolment.address
        # commit
        db.session.commit()
        # return
        return jsonify(enrolment_schema.dump(enrolment))
    # else
    else:
        # return with an error message
        return {"message": f"Enrolment with id {enrolment_id} does not exist."}, 404