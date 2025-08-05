from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(err.messages), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        if hasattr(err, "orig") and err.orig:
            if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
                return {"message": f"Required field {err.orig.diag.column_name} cannot be null."}, 400

            if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                return {"message": err.orig.diag.message_primary}, 400
        
        return {"message": "Database Integrity error has occured."}, 400
    
    @app.errorhandler(DataError)
    def handle_data_error(err):
        return {"message": err.orig.diag.message_primary}, 400
    
    @app.errorhandler(404)
    def handle_404(err):
        return {"message": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def handle_500(err):
        return {"message": "Server error occured."}, 500