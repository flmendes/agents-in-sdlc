from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        """
        Validate category name field using base validation rules.
        
        Args:
            key (str): The field name being validated.
            name (str): The category name value to validate.
            
        Returns:
            str: The validated category name value.
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        """
        Validate category description field with optional None values allowed.
        
        Args:
            key (str): The field name being validated.
            description (str | None): The description value to validate.
            
        Returns:
            str | None: The validated description value.
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self):
        """
        Return string representation of the Category object.
        
        Returns:
            str: String representation showing category name.
        """
        return f'<Category {self.name}>'
        
    def to_dict(self):
        """
        Convert Category object to dictionary representation for JSON serialization.
        
        Returns:
            dict: Dictionary containing category data including game count.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }