import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "verify_user_01"
PASSWORD = "password123"

def print_result(test_name, success, message=""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}: {message}")
    if not success:
        sys.exit(1)

def run_tests():
    # 1. Register
    requests.post(f"{BASE_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    
    # 2. Login
    resp = requests.post(f"{BASE_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    if resp.status_code != 200:
        print_result("Login", False, f"Status {resp.status_code}")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result("Auth", True, "Logged in successfully")

    # 3. Mood Swing Test
    # Send 3 Neutral entries
    entry_neutral = "I am just sitting here doing nothing special. It is a normal day."
    for i in range(3):
        requests.post(f"{BASE_URL}/journal", json={"text": entry_neutral}, headers=headers)
        time.sleep(0.5)
    
    # Send highly emotional entry
    entry_angry = "I am absolutely furious! This is the worst day of my life and I hate everything!"
    resp = requests.post(f"{BASE_URL}/journal", json={"text": entry_angry}, headers=headers)
    data = resp.json()
    if data.get("mood_swing") is True:
        print_result("Mood Swing Detection", True, f"Detected swing. Volatility logic works.")
    else:
        print_result("Mood Swing Detection", False, f"Failed to detect swing. Data: {data}")

    # 4. False Positive Test
    # Reset by logging in as different user? Or just keep going.
    # Let's use a new user for clean state
    user2 = "verify_user_02"
    requests.post(f"{BASE_URL}/register", json={"username": user2, "password": PASSWORD})
    token2 = requests.post(f"{BASE_URL}/login", json={"username": user2, "password": PASSWORD}).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    requests.post(f"{BASE_URL}/journal", json={"text": "The weather is very cloudy today."}, headers=headers2)
    resp = requests.post(f"{BASE_URL}/journal", json={"text": "Programming requires a lot of concentration."}, headers=headers2)
    # Semantically different, but both likely neutral/curiosity.
    data = resp.json()
    if data.get("mood_swing") is False:
        print_result("False Positive Check", True, f"Correctly ignored topic shift without emotion change.")
    else:
        # If emotion changed (e.g. neutral -> realization), it might trigger.
        # But if it triggers, check if it was 'neutral' -> 'neutral'.
        print_result("False Positive Check", False, f"Incorrectly flagged swing. Emotion: {data.get('emotion')}")

    # 5. Safety Test
    entry_unsafe = "I just want to end it all. I can't take this anymore."
    resp = requests.post(f"{BASE_URL}/journal", json={"text": entry_unsafe}, headers=headers)
    data = resp.json()
    if data.get("emotion") == "crisis" and "988" in data.get("reply", ""):
        print_result("Safety Protocol", True, "Correctly blocked unsafe entry and provided resources.")
    else:
        print_result("Safety Protocol", False, f"Failed to block unsafe entry. Data: {data}")

    print("\nALL PHASE 0 TESTS PASSED")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test Execution Failed: {e}")
