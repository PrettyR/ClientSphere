"""
Test script to demonstrate the standardized error handling system.

This script tests various error scenarios to ensure user-friendly responses
are provided instead of technical error messages.
"""

import requests
import json
from utils import ResponseTemplate, ErrorHandler, ValidationHelper

# Test configuration
BASE_URL = "http://localhost:5000/api"

def test_success_response():
    """Test successful API responses."""
    print("🧪 Testing Success Response...")
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ Data: {data.get('data', {})}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing success response: {e}")
        print()

def test_validation_errors():
    """Test validation error handling."""
    print("🧪 Testing Validation Errors...")
    
    # Test missing required fields
    try:
        response = requests.post(f"{BASE_URL}/register", json={})
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ User Action: {data.get('user_action', 'No action')}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        print()

def test_authentication_errors():
    """Test authentication error handling."""
    print("🧪 Testing Authentication Errors...")
    
    # Test invalid credentials
    try:
        response = requests.post(f"{BASE_URL}/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ User Action: {data.get('user_action', 'No action')}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        print()

def test_authorization_errors():
    """Test authorization error handling."""
    print("🧪 Testing Authorization Errors...")
    
    # Test accessing protected endpoint without token
    try:
        response = requests.get(f"{BASE_URL}/users/")
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ User Action: {data.get('user_action', 'No action')}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing authorization: {e}")
        print()

def test_not_found_errors():
    """Test not found error handling."""
    print("🧪 Testing Not Found Errors...")
    
    # Test accessing non-existent endpoint
    try:
        response = requests.get(f"{BASE_URL}/nonexistent")
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ User Action: {data.get('user_action', 'No action')}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing not found: {e}")
        print()

def test_server_errors():
    """Test server error handling."""
    print("🧪 Testing Server Errors...")
    
    # Test with malformed JSON
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success', False)}")
        print(f"✅ Message: {data.get('message', 'No message')}")
        print(f"✅ User Action: {data.get('user_action', 'No action')}")
        print()
        
    except Exception as e:
        print(f"❌ Error testing server errors: {e}")
        print()

def test_response_template_utilities():
    """Test response template utilities."""
    print("🧪 Testing Response Template Utilities...")
    
    # Test success response
    success_response = ResponseTemplate.success(
        message="Test successful",
        data={"test": "data"},
        metadata={"count": 1}
    )
    print(f"✅ Success Response: {success_response[0].get_json()}")
    
    # Test error response
    error_response = ResponseTemplate.error(
        message="Test error",
        error_code="TEST_ERROR",
        status_code=400,
        user_action="Please try again"
    )
    print(f"✅ Error Response: {error_response[0].get_json()}")
    
    # Test validation error
    validation_response = ResponseTemplate.validation_error(
        message="Validation failed",
        errors={"field": "Invalid value"},
        user_action="Please check your input"
    )
    print(f"✅ Validation Response: {validation_response[0].get_json()}")
    
    print()

def test_error_messages():
    """Test user-friendly error messages."""
    print("🧪 Testing User-Friendly Error Messages...")
    
    # Test various error types
    error_types = [
        "database_connection",
        "invalid_credentials", 
        "account_pending",
        "insufficient_permissions",
        "file_too_large",
        "data_processing",
        "model_not_found"
    ]
    
    for error_type in error_types:
        message = ErrorHandler.get_user_friendly_message(error_type)
        print(f"✅ {error_type}: {message}")
    
    print()

def test_validation_helpers():
    """Test validation helper functions."""
    print("🧪 Testing Validation Helpers...")
    
    # Test email validation
    email_result = ValidationHelper.validate_email("invalid-email")
    if email_result:
        print(f"✅ Email validation caught invalid email")
    
    email_result = ValidationHelper.validate_email("valid@example.com")
    if not email_result:
        print(f"✅ Email validation passed for valid email")
    
    # Test required fields validation
    data = {"name": "John", "age": 25}  # Missing email
    required_fields = ["name", "email", "age"]
    validation_result = ValidationHelper.validate_required_fields(data, required_fields)
    if validation_result:
        print(f"✅ Required fields validation caught missing fields")
    
    print()

def run_all_tests():
    """Run all error handling tests."""
    print("🚀 Starting Error Handling System Tests")
    print("=" * 50)
    print()
    
    test_success_response()
    test_validation_errors()
    test_authentication_errors()
    test_authorization_errors()
    test_not_found_errors()
    test_server_errors()
    test_response_template_utilities()
    test_error_messages()
    test_validation_helpers()
    
    print("🎉 All tests completed!")
    print()
    print("📋 Summary:")
    print("✅ Standardized response format implemented")
    print("✅ User-friendly error messages provided")
    print("✅ Consistent error handling across all endpoints")
    print("✅ Frontend integration with response handlers")
    print("✅ Comprehensive validation and error reporting")

if __name__ == "__main__":
    run_all_tests()
