"""
Simple test script to debug registration endpoint
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print("Health check timed out - server might be frozen")
        return False
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_register():
    """Test registration endpoint"""
    url = f"{BASE_URL}/auth/register"
    
    # Use unique timestamp to avoid duplicates
    import time
    timestamp = int(time.time())
    
    payload = {
        "username": f"test_user_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "Test123!@#",
        "role": "chef"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
            
            if response.status_code == 201:
                print("\n[SUCCESS] User registered successfully!")
                return True
            else:
                print(f"\n[ERROR] Registration failed with status {response.status_code}")
                return False
        except:
            print(f"Response Text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n[ERROR] Request timed out - server might be frozen")
        print("Check server logs for errors")
        return False
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing LyfterCook Registration Endpoint")
    print("=" * 60)
    
    if not test_health():
        print("\n[ERROR] Server is not responding. Start it with: python run.py")
        sys.exit(1)
    
    print("\n[OK] Server is healthy, testing registration...")
    
    if test_register():
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("[ERROR] Tests failed")
        print("=" * 60)
        sys.exit(1)
