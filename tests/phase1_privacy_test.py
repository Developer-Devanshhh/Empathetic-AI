import requests
import sys
import json
import chromadb
import os

# Adjust path to app if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "privacy_user_01"
PASSWORD = "password123"

def print_result(name, passed, msg=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {msg}")
    if not passed:
        sys.exit(1)

def run_tests():
    # 1. Register/Login
    requests.post(f"{BASE_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    resp = requests.post(f"{BASE_URL}/login", json={"username": USERNAME, "password": PASSWORD})
    if resp.status_code != 200:
        print_result("Auth", False, f"Login failed: {resp.text}")
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Client-Side Embedding (Simulated)
    # 384-dim dummy vector
    dummy_vec = [0.1] * 384
    entry_text = "Secrets of the universe."
    resp = requests.post(f"{BASE_URL}/journal", json={
        "user_id": USERNAME,
        "text": entry_text,
        "embedding": dummy_vec
    }, headers=headers)
    
    if resp.status_code != 200:
        print_result("Client Embedding API", False, f"Failed: {resp.text}")
    print_result("Client Embedding API", True, "Accepted payload with embedding")
    
    # 3. Verify Encryption (The Hard Way: Direct DB Inspection)
    # We will initialize a separate Chroma Client pointing to the same dir and read raw
    # IMPORTANT: We verify success if the text is NOT "Secrets of the universe."
    
    # We must wait a sec for FS sync potentially?
    # Actually, verify via API first (should be decrypted)
    resp = requests.get(f"{BASE_URL}/memories", headers=headers)
    mems = resp.json()
    if not mems or mems[0]["text"] != entry_text:
         print_result("Dashboard API", False, f"Failed to retrieve decrypted text. Got: {mems}")
    print_result("Dashboard API", True, "Retrieved decrypted text successfully")
         
    # Now Raw Check
    try:
        raw_client = chromadb.PersistentClient(path="./chroma_store")
        col = raw_client.get_collection("journals")
        # We need to find the doc. ID is user-uuid.
        # Just searching by metadata.
        # Wait, raw client might not have metadata if we query blindly? 
        # We can list all and check if any raw document == "Secrets of the universe."
        
        # NOTE: Collection.get() returns what's stored.
        raw_res = col.get(include=["documents"])
        
        found_plaintext = False
        for doc in raw_res["documents"]:
            if entry_text in doc:
                found_plaintext = True
                break
        
        if found_plaintext:
             print_result("Encryption at Rest", False, "Found PLAINTEXT in DB! Encryption failed.")
        else:
             print_result("Encryption at Rest", True, "No plaintext found in DB. Data is encrypted.")
             
    except Exception as e:
        print_result("Encryption Check", False, f"Could not inspect DB: {e}")

    # 4. Delete Memory
    mem_id = mems[0]["id"]
    resp = requests.delete(f"{BASE_URL}/memories/{mem_id}", headers=headers)
    if resp.status_code == 200:
        print_result("Delete API", True, "Deleted memory.")
    else:
        print_result("Delete API", False, f"Delete failed: {resp.status_code}")

    print("\nALL PRIVACY TESTS PASSED")

if __name__ == "__main__":
    run_tests()
