import requests
import json
import os

# CONFIG
BASE_URL = "http://localhost:8000"
USERNAME = "debug_user"
PASSWORD = "debug_password"

def run_test():
    print("=== STARTING SYSTEM DIAGNOSIS ===\n")

    # 1. HEALTH CHECK
    try:
        res = requests.get(f"{BASE_URL}/health")
        print(f"[*] Health Check: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"[!] Backend invalid: {e}")
        return

    # 2. REGISTER / LOGIN
    print("\n[*] Testing Auth...")
    requests.post(f"{BASE_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    
    res = requests.post(f"{BASE_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    if res.status_code != 200:
        print(f"[!] Login Failed: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[*] Auth Token acquired.")

    # 3. CREATE BOOK
    print("\n[*] Testing Book Creation...")
    res = requests.post(f"{BASE_URL}/api/books", json={"title": "Debug Book"}, headers=headers)
    if res.status_code != 200:
        print(f"[!] Create Book Failed: {res.text}")
        return
    book_id = res.json()["book_id"]
    print(f"[*] Book Created: {book_id}")

    # 4. CREATE CHAPTER
    print("\n[*] Testing Chapter Creation...")
    res = requests.post(f"{BASE_URL}/api/books/{book_id}/chapters", 
                        json={"title": "Debug Chapter"}, headers=headers)
    if res.status_code != 200:
        print(f"[!] Create Chapter Failed: {res.text}")
        return
    chapter_id = res.json()["chapter_id"]
    print(f"[*] Chapter Created: {chapter_id}")

    # 5. CREATE ENTRY (Saving)
    print("\n[*] Testing Entry Saving...")
    entry_data = {
        "chapter_id": chapter_id,
        "text": "This is a debug entry to verify database persistence.",
        "client_only": False
    }
    # Note: URL struct might be /books/{id}/entries or similar. Checking journal.py...
    # It is @router.post("/books/{book_id}/entries")
    res = requests.post(f"{BASE_URL}/api/books/{book_id}/entries", json=entry_data, headers=headers)
    if res.status_code != 200:
        print(f"[!] Save Entry Failed: {res.text}")
    else:
        print(f"[*] Entry Saved: {res.json().get('entry_id')}")

    # 6. TEST AGENTS
    print("\n[*] Testing Agents Endpoint...")
    res = requests.get(f"{BASE_URL}/api/personas")
    if res.status_code == 200:
        agents = res.json()
        print(f"[*] Agents Found: {len(agents)}")
        for a in agents:
            print(f"    - {a.get('name')} ({a.get('id')})")
    else:
        print(f"[!] Agents Endpoint Failed: {res.text}")

    print("\n=== DIAGNOSIS COMPLETE ===")

if __name__ == "__main__":
    run_test()
