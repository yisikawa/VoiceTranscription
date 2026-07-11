import uuid

import pytest
from fastapi.testclient import TestClient

import main
from config import UPLOAD_DIR

client = TestClient(main.app)


def _make_task_dir() -> str:
    task_id = str(uuid.uuid4())
    (UPLOAD_DIR / task_id).mkdir(parents=True, exist_ok=True)
    return task_id


class TestSaveEndpoint:
    def test_traversal_task_id_is_rejected(self):
        # %2e%2e は URL デコード後に ".." になる。
        # 現状は UPLOAD_DIR/.. (= backend/) が exists 判定を通ってしまう。
        res = client.post(
            "/save/%2e%2e",
            json=[{"id": 1, "start": 0.0, "end": 1.0, "text": "x"}],
        )
        assert res.status_code == 404
        # uploads の外に書き込まれていないこと
        assert not (UPLOAD_DIR.parent / "transcription_corrected.json").exists()

    def test_nonexistent_uuid_returns_404(self):
        res = client.post(
            f"/save/{uuid.uuid4()}",
            json=[{"id": 1, "start": 0.0, "end": 1.0, "text": "x"}],
        )
        assert res.status_code == 404

    def test_valid_save_writes_json(self):
        task_id = _make_task_dir()
        segments = [{"id": 1, "start": 0.0, "end": 1.5, "text": "こんにちは"}]
        res = client.post(f"/save/{task_id}", json=segments)
        assert res.status_code == 200
        saved = UPLOAD_DIR / task_id / "transcription_corrected.json"
        assert saved.exists()

    def test_invalid_body_returns_422(self):
        task_id = _make_task_dir()
        res = client.post(f"/save/{task_id}", json=[{"text": 123}])
        assert res.status_code == 422


class TestAudioEndpoint:
    def test_traversal_task_id_is_rejected(self):
        res = client.get("/audio/%2e%2e/config.py")
        assert res.status_code == 404

    def test_nonexistent_file_returns_404(self):
        task_id = _make_task_dir()
        res = client.get(f"/audio/{task_id}/nothing.wav")
        assert res.status_code == 404


class TestUploadEndpoint:
    @pytest.fixture(autouse=True)
    def no_background_processing(self, monkeypatch):
        # TestClient はレスポンス後に BackgroundTasks を同期実行するため、
        # Whisper/Demucs がロードされないようダミーに差し替える。
        async def _noop(*args, **kwargs):
            pass
        monkeypatch.setattr(main, "process_task", _noop)

    def test_rejects_unknown_extension(self):
        res = client.post("/upload", files={"file": ("evil.exe", b"MZ", "application/octet-stream")})
        assert res.status_code == 400

    def test_accepts_wav_and_saves_file(self):
        res = client.post("/upload", files={"file": ("test.wav", b"RIFF" + b"\x00" * 100, "audio/wav")})
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "processing"
        saved = UPLOAD_DIR / body["task_id"] / "test.wav"
        assert saved.exists()
        assert saved.stat().st_size == 104

    def test_oversize_returns_413_and_cleans_up(self, monkeypatch):
        monkeypatch.setattr(main, "MAX_UPLOAD_SIZE", 10)
        res = client.post("/upload", files={"file": ("big.wav", b"\x00" * 100, "audio/wav")})
        assert res.status_code == 413
        # 書きかけのタスクディレクトリが残っていないこと
        for d in UPLOAD_DIR.iterdir():
            assert not (d / "big.wav").exists()
