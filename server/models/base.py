# filepath: server/models/base.py
from . import db

class BaseModel(db.Model):
    __abstract__ = True
    
    @staticmethod
    def validate_string_length(field_name, value, min_length=2, allow_none=False):
        """
        Validate string field length with configurable constraints.
        
        Args:
            field_name (str): Name of the field being validated for error messages.
            value: The value to validate.
            min_length (int, optional): Minimum required length. Defaults to 2.
            allow_none (bool, optional): Whether None values are allowed. Defaults to False.
        
        Returns:
            str: The validated string value.
            
        Raises:
            ValueError: If validation fails due to empty value, wrong type, or insufficient length.
        """
        if value is None:
            if allow_none:
                return value
            else:
                raise ValueError(f"{field_name} cannot be empty")
        
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
            
        if len(value.strip()) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
            
        return value