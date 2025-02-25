from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from api.jwt_authorize import token_required
from model.flashcard import Flashcard
from __init__ import db

flashcard_api = Blueprint('flashcard_api', __name__, url_prefix='/api')

# ✅ Correctly enable CORS with credentials support
CORS(
    flashcard_api,
    resources={r"/*": {"origins": "http://127.0.0.1:4887"}},
    supports_credentials=True
)

api = Api(flashcard_api)

class FlashcardAPI:
    class _CRUD(Resource):
        @token_required()
        @cross_origin(origins="http://127.0.0.1:4887", supports_credentials=True)
        def post(self):
            """Create a new flashcard."""
            current_user = g.current_user
            data = request.get_json()
            print(f"🔍 Received POST data: {data}")  # Debug log

            if not data or 'title' not in data or 'content' not in data or 'deck_id' not in data:
                return {'message': 'Title, content, and deck_id are required'}, 400

            flashcard = Flashcard(data['title'], data['content'], current_user.id, data['deck_id'])
            flashcard = flashcard.create()

            if not flashcard:
                print("⚠️ Failed to create flashcard!")  # Debug log
                return {'message': 'Failed to create flashcard'}, 400

            print(f"✅ Flashcard created successfully: {flashcard.read()}")  # Debug log
            return jsonify(flashcard.read())

        @token_required()
        @cross_origin(origins="http://127.0.0.1:4887", supports_credentials=True)
        def get(self):
            """Get all flashcards for the current user."""
            current_user = g.current_user
            print(f"🔍 Fetching flashcards for user ID: {current_user.id}")  # Debug log

            flashcards = Flashcard.query.filter_by(_user_id=current_user.id).all()
            flashcard_list = [flashcard.read() for flashcard in flashcards]

            print(f"✅ Found {len(flashcard_list)} flashcards.")  # Debug log
            return jsonify(flashcard_list)

        @token_required()
        @cross_origin(origins="http://127.0.0.1:4887", supports_credentials=True)
        def put(self, flashcard_id):
            """Update an existing flashcard."""
            print(f"🔍 PUT Request for flashcard_id: {flashcard_id}")  # Debug log
            data = request.get_json()
            if not data:
                return {'message': 'Request body is missing'}, 400

            flashcard = Flashcard.query.filter_by(id=flashcard_id).first()  # ✅ FIXED

            if not flashcard:
                print(f"⚠️ Flashcard ID {flashcard_id} not found!")  # Debug log
                return {'message': 'Flashcard not found'}, 404

            if flashcard._user_id != g.current_user.id:
                print(f"⛔ Unauthorized update attempt by user {g.current_user.id}")  # Debug log
                return {'message': 'Unauthorized'}, 403

            # Update fields
            flashcard.title = data.get('title', flashcard.title)
            flashcard.content = data.get('content', flashcard.content)

            try:
                db.session.commit()  # ✅ Ensure the update is saved
                print(f"✅ Flashcard {flashcard_id} updated successfully.")  # Debug log
                return jsonify(flashcard.read())
            except Exception as e:
                db.session.rollback()  # Rollback on error
                print(f"🔥 ERROR updating flashcard {flashcard_id}: {e}")  # Debug log
                return {'message': 'Failed to update flashcard', 'error': str(e)}, 500

        @token_required()
        @cross_origin(origins="http://127.0.0.1:4887", supports_credentials=True)
        def delete(self, flashcard_id):
            """Delete a flashcard."""
            print(f"🔍 DELETE Request for flashcard_id: {flashcard_id}")  # Debug log

            flashcard = Flashcard.query.filter_by(id=flashcard_id).first()  # ✅ FIXED

            if not flashcard:
                print(f"⚠️ Flashcard ID {flashcard_id} not found!")  # Debug log
                return {'message': 'Flashcard not found'}, 404

            if flashcard._user_id != g.current_user.id:
                print(f"⛔ Unauthorized delete attempt by user {g.current_user.id}")  # Debug log
                return {'message': 'Unauthorized'}, 403

            try:
                db.session.delete(flashcard)
                db.session.commit()
                print(f"✅ Flashcard {flashcard_id} deleted successfully.")  # Debug log
                return {'message': 'Flashcard deleted successfully'}, 200
            except Exception as e:
                db.session.rollback()
                print(f"🔥 ERROR deleting flashcard {flashcard_id}: {e}")  # Debug log
                return {'message': 'Failed to delete flashcard', 'error': str(e)}, 500

    # ✅ Handle OPTIONS requests for preflight
    @flashcard_api.route('/flashcard/<int:flashcard_id>', methods=['OPTIONS'])
    @cross_origin(origins="http://127.0.0.1:4887", supports_credentials=True)
    def flashcard_options(flashcard_id):
        return '', 204  # Return an empty 204 response for preflight

api.add_resource(FlashcardAPI._CRUD, '/flashcard', '/flashcard/<int:flashcard_id>')
