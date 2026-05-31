import os
import tempfile
import unittest
from unittest.mock import patch

try:
    import flask  # noqa: F401
    import requests
except ImportError:
    flask = None
    requests = None

if flask is not None and requests is not None:
    import app as web_app


@unittest.skipIf(flask is None or requests is None, "Flask web dependencies are not installed")
class AppTest(unittest.TestCase):
    def setUp(self):
        web_app.set_progress("idle", "Idle")
        web_app.user_config = web_app.DEFAULT_CONFIG.copy()
        self.client = web_app.app.test_client()

    def test_models_requires_post_json_body(self):
        self.assertEqual(405, self.client.get("/api/models").status_code)
        self.assertEqual(400, self.client.post("/api/models").status_code)

    def test_models_passes_credentials_in_json_body(self):
        with patch.object(web_app, "fetch_models", return_value={"video": [], "llm": []}) as fetch:
            response = self.client.post(
                "/api/models",
                json={"api_url": "https://example.com/v1/", "api_key": "secret"},
            )

        self.assertEqual(200, response.status_code)
        fetch.assert_called_once_with("https://example.com/v1/", "secret")

    def test_generate_rejects_unsupported_mode(self):
        response = self.client.post("/api/gen", json={"mode": "unknown"})

        self.assertEqual(400, response.status_code)
        self.assertEqual("Unsupported mode", response.json["err"])

    def test_generate_rejects_invalid_duration(self):
        response = self.client.post("/api/gen", json={"mode": "classic", "duration": 0})

        self.assertEqual(400, response.status_code)
        self.assertEqual("时长必须在 1 到 300 秒之间", response.json["err"])

    def test_generate_rejects_concurrent_task(self):
        web_app.set_progress("run", "Running")

        response = self.client.post("/api/gen", json={"mode": "classic"})

        self.assertEqual(409, response.status_code)
        self.assertEqual("Already running", response.json["err"])

    def test_download_video_removes_partial_file_on_error(self):
        class FailedResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def raise_for_status(self):
                raise requests.HTTPError("download failed")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "video.mp4")
            with patch.object(web_app.requests, "get", return_value=FailedResponse()):
                with self.assertRaises(requests.HTTPError):
                    web_app.download_video("https://example.com/video.mp4", output_path)

            self.assertFalse(os.path.exists(output_path))

    def test_build_url_removes_duplicate_slashes(self):
        self.assertEqual("https://example.com/v1/models", web_app.build_url("https://example.com/v1/", "/models"))


if __name__ == "__main__":
    unittest.main()
