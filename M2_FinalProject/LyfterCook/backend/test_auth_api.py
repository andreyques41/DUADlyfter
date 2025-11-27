"""
Test Authentication Endpoints
Quick script to test auth endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint."""
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_register():
    """Test user registration."""
    print("\n2. Testing POST /auth/register...")
    payload = {
        "username": "chef_john",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "role": "chef"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_login():
    """Test user login."""
    print("\n3. Testing POST /auth/login...")
    payload = {
        "username": "chef_john",
        "password": "SecurePass123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            return result.get('data', {}).get('token')
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def test_get_me(token):
    """Test get current user with JWT."""
    print("\n4. Testing GET /auth/me (protected route)...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_protected_without_token():
    """Test protected route without token."""
    print("\n5. Testing GET /auth/me (WITHOUT token)...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LyfterCook Authentication API Tests")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n[ERROR] Health check failed! Is the server running?")
        exit(1)
    
    print("\n[SUCCESS] Server is running!")
    
    # Test registration
    if test_register():
        print("\n[SUCCESS] Registration successful!")
    else:
        print("\n[WARNING] Registration failed (might be duplicate user - continuing...)")
    
    # Test login
    token = test_login()
    if token:
        print(f"\n[SUCCESS] Login successful! Token: {token[:20]}...")
    else:
        print("\n[ERROR] Login failed!")
        exit(1)
    
    # Test protected route with token
    if test_get_me(token):
        print("\n[SUCCESS] Protected route access successful!")
    else:
        print("\n[ERROR] Protected route access failed!")
    
    # Test protected route without token
    if test_protected_without_token():
        print("\n[SUCCESS] Protected route correctly rejects requests without token!")
    else:
        print("\n[ERROR] Protected route security issue!")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
