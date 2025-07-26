from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from sqlalchemy.exc import IntegrityError

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limit max per_page to prevent abuse
        per_page = 20
    
    # Use the base query for all games
    base_query = get_games_base_query()
    
    # Get total count
    total = base_query.count()
    
    # Apply pagination
    games_query = base_query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_query]
    
    # Calculate pagination metadata
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    # Return paginated response
    return jsonify({
        'data': games_list,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages
    })

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)

@games_bp.route('/api/games', methods=['POST'])
def create_game() -> tuple[Response, int] | Response:
    try:
        # Parse JSON payload
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400
            
        if not data:
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'category_id', 'publisher_id']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate foreign key references
        publisher = db.session.get(Publisher, data['publisher_id'])
        if not publisher:
            return jsonify({"error": "Publisher not found"}), 404
            
        category = db.session.get(Category, data['category_id'])
        if not category:
            return jsonify({"error": "Category not found"}), 404
        
        # Create new game
        game = Game(
            title=data['title'],
            description=data['description'],
            publisher_id=data['publisher_id'],
            category_id=data['category_id'],
            star_rating=data.get('star_rating')  # Optional field
        )
        
        # Add to database
        db.session.add(game)
        db.session.commit()
        
        # Return created game
        created_game = get_games_base_query().filter(Game.id == game.id).first()
        return jsonify(created_game.to_dict()), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['PUT'])
def update_game(id: int) -> tuple[Response, int] | Response:
    try:
        # Check if game exists
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Parse JSON payload
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON format"}), 400
            
        if not data:
            return jsonify({"error": "Request body cannot be empty"}), 400
        
        # Validate foreign key references if provided
        if 'publisher_id' in data:
            publisher = db.session.get(Publisher, data['publisher_id'])
            if not publisher:
                return jsonify({"error": "Publisher not found"}), 404
            game.publisher_id = data['publisher_id']
                
        if 'category_id' in data:
            category = db.session.get(Category, data['category_id'])
            if not category:
                return jsonify({"error": "Category not found"}), 404
            game.category_id = data['category_id']
        
        # Update fields if provided
        if 'title' in data:
            game.title = data['title']
        if 'description' in data:
            game.description = data['description']
        if 'star_rating' in data:
            game.star_rating = data['star_rating']
        
        # Save changes
        db.session.commit()
        
        # Return updated game
        updated_game = get_games_base_query().filter(Game.id == id).first()
        return jsonify(updated_game.to_dict())
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database constraint violation"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@games_bp.route('/api/games/<int:id>', methods=['DELETE'])
def delete_game(id: int) -> tuple[Response, int] | Response:
    try:
        # Check if game exists
        game = db.session.get(Game, id)
        if not game:
            return jsonify({"error": "Game not found"}), 404
        
        # Delete the game
        db.session.delete(game)
        db.session.commit()
        
        # Return success message
        return jsonify({"message": "Game deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
