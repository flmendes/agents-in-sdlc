import unittest
import json
from typing import Dict, List, Any, Optional
from flask import Flask, Response
from models import Game, Publisher, Category, db, init_db
from routes.games import games_bp

class TestGamesRoutes(unittest.TestCase):
    # Test data as complete objects
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc"},
            {"name": "Scrum Masters"}
        ],
        "categories": [
            {"name": "Strategy"},
            {"name": "Card Game"}
        ],
        "games": [
            {
                "title": "Pipeline Panic",
                "description": "Build your DevOps pipeline before chaos ensues",
                "publisher_index": 0,
                "category_index": 0,
                "star_rating": 4.5
            },
            {
                "title": "Agile Adventures",
                "description": "Navigate your team through sprints and releases",
                "publisher_index": 1,
                "category_index": 1,
                "star_rating": 4.2
            }
        ]
    }
    
    # API paths
    GAMES_API_PATH: str = '/api/games'

    def setUp(self) -> None:
        """Set up test database and seed data"""
        # Create a fresh Flask app for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Register the games blueprint
        self.app.register_blueprint(games_bp)
        
        # Initialize the test client
        self.client = self.app.test_client()
        
        # Initialize in-memory database for testing
        init_db(self.app, testing=True)
        
        # Create tables and seed data
        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Helper method to seed test data"""
        # Create test publishers
        publishers = [
            Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]
        ]
        db.session.add_all(publishers)
        
        # Create test categories
        categories = [
            Category(**category_data) for category_data in self.TEST_DATA["categories"]
        ]
        db.session.add_all(categories)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create test games
        games = []
        for game_data in self.TEST_DATA["games"]:
            game_dict = game_data.copy()
            publisher_index = game_dict.pop("publisher_index")
            category_index = game_dict.pop("category_index")
            
            games.append(Game(
                **game_dict,
                publisher=publishers[publisher_index],
                category=categories[category_index]
            ))
            
        db.session.add_all(games)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Helper method to parse response data"""
        return json.loads(response.data)

    def test_get_games_success(self) -> None:
        """Test successful retrieval of multiple games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        # Verify all games using loop instead of manual testing
        for i, game_data in enumerate(data):
            test_game = self.TEST_DATA["games"][i]
            test_publisher = self.TEST_DATA["publishers"][test_game["publisher_index"]]
            test_category = self.TEST_DATA["categories"][test_game["category_index"]]
            
            self.assertEqual(game_data['title'], test_game["title"])
            self.assertEqual(game_data['publisher']['name'], test_publisher["name"])
            self.assertEqual(game_data['category']['name'], test_category["name"])
            self.assertEqual(game_data['starRating'], test_game["star_rating"])

    def test_get_games_structure(self) -> None:
        """Test the response structure for games"""
        # Act
        response = self.client.get(self.GAMES_API_PATH)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(self.TEST_DATA["games"]))
        
        required_fields = ['id', 'title', 'description', 'publisher', 'category', 'starRating']
        for field in required_fields:
            self.assertIn(field, data[0])

    def test_get_game_by_id_success(self) -> None:
        """Test successful retrieval of a single game by ID"""
        # Get the first game's ID from the list endpoint
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        first_game = self.TEST_DATA["games"][0]
        first_publisher = self.TEST_DATA["publishers"][first_game["publisher_index"]]
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], first_game["title"])
        self.assertEqual(data['publisher']['name'], first_publisher["name"])
        
    def test_get_game_by_id_not_found(self) -> None:
        """Test retrieval of a non-existent game by ID"""
        # Act
        response = self.client.get(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

    # CREATE game tests
    def test_create_game_success(self) -> None:
        """Test successful creation of a new game"""
        # Arrange
        new_game_data = {
            "title": "New Test Game",
            "description": "A great new game for testing purposes",
            "publisher_id": 1,
            "category_id": 1,
            "star_rating": 4.8
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  json=new_game_data,
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['title'], new_game_data['title'])
        self.assertEqual(data['description'], new_game_data['description'])
        self.assertEqual(data['starRating'], new_game_data['star_rating'])
        self.assertIsNotNone(data['id'])
        
    def test_create_game_missing_required_fields(self) -> None:
        """Test game creation with missing required fields"""
        # Arrange
        incomplete_game_data = {
            "title": "Incomplete Game"
            # Missing description, publisher_id, category_id
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  json=incomplete_game_data,
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", data['error'])
        
    def test_create_game_invalid_publisher(self) -> None:
        """Test game creation with non-existent publisher"""
        # Arrange
        game_data = {
            "title": "Test Game",
            "description": "A game with invalid publisher",
            "publisher_id": 999,  # Non-existent publisher
            "category_id": 1
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  json=game_data,
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Publisher not found")
        
    def test_create_game_invalid_category(self) -> None:
        """Test game creation with non-existent category"""
        # Arrange
        game_data = {
            "title": "Test Game",
            "description": "A game with invalid category",
            "publisher_id": 1,
            "category_id": 999  # Non-existent category
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  json=game_data,
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Category not found")
        
    def test_create_game_invalid_json(self) -> None:
        """Test game creation with invalid JSON"""
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  data="invalid json",
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        
    def test_create_game_no_content_type(self) -> None:
        """Test game creation without JSON content type"""
        # Arrange
        game_data = {
            "title": "Test Game",
            "description": "A test game",
            "publisher_id": 1,
            "category_id": 1
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, data=game_data)
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], "Content-Type must be application/json")
        
    def test_create_game_validation_error(self) -> None:
        """Test game creation with validation errors"""
        # Arrange - title too short (less than 2 characters)
        game_data = {
            "title": "A",  # Too short
            "description": "Valid description that is long enough",
            "publisher_id": 1,
            "category_id": 1
        }
        
        # Act
        response = self.client.post(self.GAMES_API_PATH, 
                                  json=game_data,
                                  content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("Game title must be at least", data['error'])
        
    # UPDATE game tests
    def test_update_game_success(self) -> None:
        """Test successful update of an existing game"""
        # Get the first game's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Arrange
        update_data = {
            "title": "Updated Game Title",
            "star_rating": 5.0
        }
        
        # Act
        response = self.client.put(f'{self.GAMES_API_PATH}/{game_id}', 
                                 json=update_data,
                                 content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], update_data['title'])
        self.assertEqual(data['starRating'], update_data['star_rating'])
        
    def test_update_game_not_found(self) -> None:
        """Test update of a non-existent game"""
        # Arrange
        update_data = {
            "title": "Updated Title"
        }
        
        # Act
        response = self.client.put(f'{self.GAMES_API_PATH}/999', 
                                 json=update_data,
                                 content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")
        
    def test_update_game_invalid_publisher(self) -> None:
        """Test game update with non-existent publisher"""
        # Get the first game's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Arrange
        update_data = {
            "publisher_id": 999  # Non-existent publisher
        }
        
        # Act
        response = self.client.put(f'{self.GAMES_API_PATH}/{game_id}', 
                                 json=update_data,
                                 content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Publisher not found")
        
    def test_update_game_invalid_category(self) -> None:
        """Test game update with non-existent category"""
        # Get the first game's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Arrange
        update_data = {
            "category_id": 999  # Non-existent category
        }
        
        # Act
        response = self.client.put(f'{self.GAMES_API_PATH}/{game_id}', 
                                 json=update_data,
                                 content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Category not found")
        
    def test_update_game_validation_error(self) -> None:
        """Test game update with validation errors"""
        # Get the first game's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Arrange - description too short
        update_data = {
            "description": "Short"  # Less than 10 characters
        }
        
        # Act
        response = self.client.put(f'{self.GAMES_API_PATH}/{game_id}', 
                                 json=update_data,
                                 content_type='application/json')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("Description must be at least", data['error'])
        
    # DELETE game tests
    def test_delete_game_success(self) -> None:
        """Test successful deletion of an existing game"""
        # Get the first game's ID
        response = self.client.get(self.GAMES_API_PATH)
        games = self._get_response_data(response)
        game_id = games[0]['id']
        
        # Act
        response = self.client.delete(f'{self.GAMES_API_PATH}/{game_id}')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Game deleted successfully")
        
        # Verify game is actually deleted
        response = self.client.get(f'{self.GAMES_API_PATH}/{game_id}')
        self.assertEqual(response.status_code, 404)
        
    def test_delete_game_not_found(self) -> None:
        """Test deletion of a non-existent game"""
        # Act
        response = self.client.delete(f'{self.GAMES_API_PATH}/999')
        data = self._get_response_data(response)
        
        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['error'], "Game not found")

if __name__ == '__main__':
    unittest.main()