"""手動E2Eスクリプト（pytestではない）。
使い方: python test_backend.py <音声または動画ファイルのパス>
バックエンド (http://localhost:8001) が起動している状態で実行する。
"""
import requests
import time
import os
import sys

API_URL = "http://localhost:8001"


def test_api(test_file: str):
    print(f"Testing API at {API_URL}")

    # 1. Upload
    print(f"Uploading {test_file}...")
    with open(test_file, "rb") as f:
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
    if len(sys.argv) < 2:
        print("使い方: python test_backend.py <音声または動画ファイルのパス>")
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"Test file not found: {sys.argv[1]}")
        sys.exit(1)
    test_api(sys.argv[1])
