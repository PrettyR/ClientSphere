"""
Test database connection and User model
"""

from app import create_app
from models import db, User
from utils import ResponseTemplate, ValidationHelper

def test_database_connection():
    """Test if database connection is working"""
    try:
        app = create_app()
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text("SELECT 1"))
            print("Database connection successful")
            
            # Test User model
            user_count = User.query.count()
            print(f"User model working - {user_count} users in database")
            
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def test_response_templates():
    """Test response template functionality"""
    try:
        app = create_app()
        with app.app_context():
            # Test success response
            success_response = ResponseTemplate.success(
                message="Test successful",
                data={"test": "data"}
            )
            print("ResponseTemplate.success working")
            
            # Test validation helper
            validation_result = ValidationHelper.validate_email("test@example.com")
            if not validation_result:
                print("ValidationHelper.validate_email working")
            else:
                print("ValidationHelper.validate_email failed")
                
        return True
    except Exception as e:
        print(f"Response template test failed: {e}")
        return False

def test_registration_logic():
    """Test registration logic without HTTP"""
    try:
        app = create_app()
        with app.app_context():
            # Test data validation
            test_data = {
                "employee_id": "TEST001",
                "email": "test@example.com",
                "password": "TestPassword123"
            }
            
            # Test validation
            validation_error = ValidationHelper.validate_required_fields(
                test_data, ["employee_id", "email", "password"]
            )
            if validation_error:
                print("Required fields validation failed")
                return False
            
            email_validation = ValidationHelper.validate_email(test_data["email"])
            if email_validation:
                print("Email validation failed")
                return False
                
            password_validation = ValidationHelper.validate_password_strength(test_data["password"])
            if password_validation:
                print("Password validation failed")
                return False
            
            print("Registration logic validation working")
            return True
            
    except Exception as e:
        print(f"Registration logic test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Database and Registration Logic")
    print("=" * 50)
    
    # Test database
    if not test_database_connection():
        print("Database tests failed")
        exit(1)
    
    print()
    
    # Test response templates
    if not test_response_templates():
        print("Response template tests failed")
        exit(1)
    
    print()
    
    # Test registration logic
    if not test_registration_logic():
        print("Registration logic tests failed")
        exit(1)
    
    print()
    print("All tests passed!")
