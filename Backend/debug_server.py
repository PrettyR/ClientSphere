"""
Debug script to test the server and registration endpoint
"""

import requests
import json

def test_server_health():
    """Test if the server is running and responding"""
    try:
        response = requests.get("http://localhost:5000/")
        print(f"Server Health Check:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Server Health Check Failed: {e}")
        return False

def test_registration_endpoint():
    """Test the registration endpoint with sample data"""
    try:
        test_data = {
            "employee_id": "TEST001",
            "email": "test@example.com",
            "password": "TestPassword123",
            "confirm_password": "TestPassword123",
            "role": "employee"
        }
        
        print(f"Testing Registration Endpoint:")
        print(f"   Data: {test_data}")
        
        response = requests.post(
            "http://localhost:5000/api/register",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"Registration Test Failed: {e}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    try:
        response = requests.options(
            "http://localhost:5000/api/register",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"Testing CORS Headers:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Check for duplicate CORS headers
        origin_headers = [v for k, v in response.headers.items() if k.lower() == 'access-control-allow-origin']
        if len(origin_headers) > 1:
            print(f"   Duplicate CORS headers found: {origin_headers}")
            return False
        else:
            print(f"   CORS headers look good")
            return True
            
    except Exception as e:
        print(f"CORS Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting Server Debug Tests")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("Server is not running. Please start the server first.")
        exit(1)
    
    print()
    
    # Test CORS
    test_cors_headers()
    
    print()
    
    # Test registration
    test_registration_endpoint()
    
    print()
    print("Debug tests completed!")
