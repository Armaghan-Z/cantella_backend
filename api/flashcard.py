from flask import Blueprint, request, jsonify
from model.flashcard import Flashcard
from __init__ import db
from api.jwt_authorize import token_required

flashcard_api = Blueprint('flashcard_api', __name__, url_prefix='/api/flashcard')

@flashcard_api.route('', methods=['POST'])
@token_required()
def create_flashcard():
    """Create a new flashcard."""
    data = request.json
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')
    deck_id = data.get('deck_id')

    if not title or not content or not deck_id or not user_id:
        return jsonify({"error": "Title, content, user ID, and deck ID are required."}), 400

    try:
        flashcard = Flashcard(title=title, content=content, user_id=user_id, deck_id=deck_id)
        flashcard.create()
        return jsonify(flashcard.read()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flashcard_api.route('/<int:flashcard_id>', methods=['GET'])
def get_flashcard(flashcard_id):
    """Retrieve a single flashcard."""
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard:
        return jsonify({"error": "Flashcard not found."}), 404
    return jsonify(flashcard.read()), 200

@flashcard_api.route('', methods=['GET'])
@token_required()
def get_all_flashcards():
    """Retrieve all flashcards for the current user."""
    flashcards = Flashcard.query.all()
    return jsonify([flashcard.read() for flashcard in flashcards]), 200

@flashcard_api.route('/<int:flashcard_id>', methods=['PUT'])
@token_required()
def update_flashcard(flashcard_id):
    """Update a specific flashcard."""
    data = request.json
    flashcard = Flashcard.query.get(flashcard_id)

    if not flashcard:
        return jsonify({"error": "Flashcard not found."}), 404

    if "title" in data:
        flashcard._title = data["title"]
    if "content" in data:
        flashcard._content = data["content"]

    try:
        db.session.commit()
        return jsonify(flashcard.read()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@flashcard_api.route('/<int:flashcard_id>', methods=['DELETE'])
@token_required()
def delete_flashcard(flashcard_id):
    """Delete a flashcard."""
    flashcard = Flashcard.query.get(flashcard_id)

    if not flashcard:
        return jsonify({"error": "Flashcard not found."}), 404

    try:
        flashcard.delete()
        return jsonify({"message": f"Flashcard with ID {flashcard_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
