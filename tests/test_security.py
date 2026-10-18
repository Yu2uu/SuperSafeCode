"""Run against Flask locally, or the container with NOTES_TEST_URL set."""

import importlib.util
import gc
import json
import os
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


class SecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = os.environ.get("NOTES_TEST_URL")
        cls.api_key = os.environ["NOTES_API_KEY"] if cls.base_url else "security-test-only"
        if cls.base_url:
            return
        cls.saved_env = {key: os.environ.get(key) for key in ("NOTES_API_KEY", "NOTES_DB_PATH")}
        cls.temp = tempfile.TemporaryDirectory()
        os.environ["NOTES_API_KEY"] = cls.api_key
        os.environ["NOTES_DB_PATH"] = str(Path(cls.temp.name) / "notes.db")
        source = Path(os.environ.get("NOTES_TEST_SOURCE", "app/main.py"))
        spec = importlib.util.spec_from_file_location("notes_under_test", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.app.config["TESTING"] = True
        cls.client = module.app.test_client()

    @classmethod
    def tearDownClass(cls):
        if not cls.base_url:
            for key, value in cls.saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            gc.collect()
            cls.temp.cleanup()

    def request(self, method, path, key=None, body=None):
        headers = {}
        if key is not None:
            headers["X-API-Key"] = key
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.base_url:
            data = json.dumps(body).encode() if body is not None else None
            req = Request(self.base_url + path, data=data, headers=headers, method=method)
            try:
                response = urlopen(req, timeout=5)
            except HTTPError as error:
                response = error
            with response:
                raw = response.read()
                body = json.loads(raw) if "application/json" in response.headers.get("Content-Type", "") else None
                return response.status, response.headers, body
        response = self.client.open(path, method=method, headers=headers, json=body)
        return response.status_code, response.headers, response.get_json()

    def create_note(self):
        status, _, payload = self.request(
            "POST", "/notes", self.api_key, {"owner": "test-owner", "body": "test-body"}
        )
        self.assertEqual(status, 201)
        return payload["id"]

    def test_health_is_public(self):
        status, _, body = self.request("GET", "/healthz")
        self.assertEqual((status, body), (200, {"status": "ok"}))

    def test_create_and_retrieve(self):
        note_id = self.create_note()
        status, _, body = self.request("GET", f"/notes/{note_id}", self.api_key)
        self.assertEqual(status, 200)
        self.assertEqual(body, {"id": note_id, "owner": "test-owner", "body": "test-body"})

    def test_get_requires_authentication(self):
        note_id = self.create_note()
        for key in (None, "", "incorrect-key"):
            with self.subTest(key=key):
                status, _, body = self.request("GET", f"/notes/{note_id}", key)
                self.assertEqual(status, 401)
                self.assertNotIn("body", body)

    def test_post_requires_authentication(self):
        for key in (None, "", "incorrect-key"):
            with self.subTest(key=key):
                status, _, _ = self.request("POST", "/notes", key, {"owner": "x", "body": "y"})
                self.assertEqual(status, 401)

    def test_injection_cannot_select_existing_note(self):
        self.create_note()
        for value in ("-1 OR 1=1", "-1 UNION SELECT 1, 'injected', 'data' --"):
            with self.subTest(value=value):
                status, _, body = self.request("GET", "/notes/" + quote(value, safe=""), self.api_key)
                self.assertEqual((status, body), (404, {"error": "not found"}))

    def test_headers_on_success_and_errors(self):
        for path, key, expected in (
            ("/healthz", None, 200),
            ("/notes/-1", None, 401),
            ("/notes/-1", self.api_key, 404),
            ("/missing", None, 404),
        ):
            with self.subTest(path=path, authenticated=key is not None):
                status, headers, _ = self.request("GET", path, key)
                self.assertEqual(status, expected)
                self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
                self.assertEqual(headers.get("Cache-Control"), "no-store")
                self.assertEqual(headers.get("X-Frame-Options"), "DENY")
                self.assertEqual(headers.get("Content-Security-Policy"), "default-src 'none'; frame-ancestors 'none'")

    def test_invalid_payload_rejected(self):
        for body in ({}, [], "text", {"owner": 12, "body": "x"}):
            with self.subTest(body=body):
                status, _, _ = self.request("POST", "/notes", self.api_key, body)
                self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
