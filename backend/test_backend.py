import requests
import time
import os

API_URL = "http://localhost:8001"
# Use a small file for testing
TEST_FILE = r"d:\AntiGravity\LyricSyncAI\demo3.mp4"

def test_api():
    print(f"Testing API at {API_URL}")
    
    # 1. Upload
    print(f"Uploading {TEST_FILE}...")
    with open(TEST_FILE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    
    task_id = response.json()["task_id"]
    print(f"Upload successful. Task ID: {task_id}")
    
    # 2. Poll Status
    print("Polling status...")
    while True:
        status_response = requests.get(f"{API_URL}/tasks/{task_id}")
        if status_response.status_code != 200:
            print(f"Status check failed: {status_response.text}")
            break
            
        status = status_response.json()
        print(f"Status: {status['status']}")
        
        if status["status"] == "completed":
            print("Processing complete!")
            print(f"Result: {status['result'].keys()}")
            print(f"Transcription segments: {len(status['result']['transcription']['segments'])}")
            break
        elif status["status"] == "failed":
            print(f"Processing failed: {status.get('error')}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    if not os.path.exists(TEST_FILE):
        print(f"Test file not found: {TEST_FILE}")
    else:
        test_api()
