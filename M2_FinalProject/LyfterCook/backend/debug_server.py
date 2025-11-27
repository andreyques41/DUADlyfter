"""
Debug script to test server endpoints step by step
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_endpoint(method, url, data=None, timeout=5):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            print(f"Payload: {json.dumps(data, indent=2)}")
            response = requests.post(url, json=data, timeout=timeout)
        
        print(f"Status: {response.status_code}")
        
        try:
            response_json = response.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text[:500]}")
        
        return response.status_code < 400
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out!")
        print("Server might be frozen or stuck in infinite loop")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection refused!")
        print("Is the server running? Start with: python run.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("\n" + "="*60)
    print("LyfterCook Server Debug Tests")
    print("="*60)
    
    # Test 1: Health check
    print("\n[TEST 1] Health Check")
    if not test_endpoint("GET", f"{BASE_URL}/health"):
        print("\n[FATAL] Server not responding. Exiting.")
        return
    
    time.sleep(1)
    
    # Test 2: Test endpoint
    print("\n[TEST 2] Test Endpoint (GET)")
    if not test_endpoint("GET", f"{BASE_URL}/test"):
        print("\n[ERROR] Test endpoint failed")
    
    time.sleep(1)
    
    # Test 3: Test endpoint with POST
    print("\n[TEST 3] Test Endpoint (POST)")
    test_data = {"test": "data"}
    if not test_endpoint("POST", f"{BASE_URL}/test", test_data):
        print("\n[ERROR] Test POST failed")
    
    time.sleep(1)
    
    # Test 4: Registration
    print("\n[TEST 4] User Registration")
    timestamp = int(time.time())
    registration_data = {
        "username": f"debug_user_{timestamp}",
        "email": f"debug_{timestamp}@test.com",
        "password": "Test123!@#",
        "role": "chef"
    }
    
    success = test_endpoint("POST", f"{BASE_URL}/auth/register", registration_data, timeout=10)
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] All tests passed!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("[ERROR] Registration test failed")
        print("Check server console for error messages")
        print("="*60)

if __name__ == "__main__":
    main()
