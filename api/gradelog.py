from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from api.jwt_authorize import token_required
from __init__ import db
from model.gradelog import GradeLog

# Blueprint and API
gradelog_api = Blueprint('gradelog_api', __name__, url_prefix='/api')
api = Api(gradelog_api)

class GradelogAPI:
    class _CRUD(Resource):
        @token_required()
        def post(self):
            """Create a new grade entry."""
            current_user = g.current_user
            data = request.get_json()

            # Validate input
            if not data or 'subject' not in data or 'grade' not in data:
                return {"message": "Subject and grade are required"}, 400
            
            # Create a new grade log
            new_grade_log = GradeLog(
                user_id=current_user.id,
                subject=data['subject'],
                grade=data['grade'],
                notes=data.get('notes', '')
            )
            created_log = new_grade_log.create()
            if created_log:
                return {"message": "Grade logged successfully", "grade_log_id": created_log.id}, 201
            return {"message": "Failed to create grade log"}, 500

        @token_required()
        def get(self):
            """Get all grade entries for the current user."""
            current_user = g.current_user
            all_gradelogs = GradeLog.query.all()
            gradelog = []

            for log in all_gradelogs:
                gradelog.append(log.read())

            return jsonify(gradelog)

        @token_required()
        def put(self):
            """Update an existing grade log."""
            data = request.get_json()
            if not data or 'id' not in data:
                return {"message": "Grade Log ID is required"}, 400
            grade_log = GradeLog.query.get(data['id'])
            if not grade_log or grade_log.user_id != g.current_user.id:
                return {"message": "Grade Log not found or unauthorized"}, 404
            updated_log = grade_log.update(data)
            return updated_log.read(), 200

        @token_required()
        def delete(self):
            """Delete a grade log."""
            grade_log_id = request.args.get('id')
            if not grade_log_id or not grade_log_id.isdigit():
                return {"message": "A valid Grade Log ID is required"}, 400

            grade_log = GradeLog.query.get(int(grade_log_id))
            if not grade_log or grade_log.user_id != g.current_user.id:
                return {"message": "Grade Log not found or unauthorized"}, 404

            try:
                grade_log.delete()
                return {"message": "Grade Log deleted successfully"}, 200
            except Exception as e:
                return {"message": f"An error occurred: {str(e)}"}, 500
            
        @staticmethod
        def restore(data):
            for log_data in data:
                _ = log_data.pop('id', None)
            id = log_data.get("id", None)
            user_id = log_data.get("user_id", None)
            subject = log_data.get("subject", None)
            grade = log_data.get("grade", None)
            notes = log_data.get("notes", None)
            date = log_data.get("date", None)
            gradelog = GradeLog.query.filter_by(id=id, user_id=user_id, subject=subject, grade=grade, notes=notes, date=date ).first()
            if gradelog:
                gradelog.update(log_data)
            else:
                gradelog = GradeLog(**log_data)
                gradelog.create()
            db.session.commit() 


# Register the resource
api.add_resource(GradelogAPI._CRUD, '/gradelog')
