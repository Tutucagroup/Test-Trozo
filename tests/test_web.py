import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from product_tester.web import App, make_handler


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.app = App(workspace=d / "ws", runs_dir=d / "runs")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.app))
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def req(self, path, data=None, headers=None, raw=False):
        body = data if raw else (json.dumps(data).encode() if data is not None else None)
        r = urllib.request.Request(self.base + path, data=body, headers=headers or {})
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def test_index(self):
        code, body = self.req("/")
        self.assertEqual(code, 200)
        self.assertIn(b"Product Tester", body)

    def test_upload_sanitizes_name(self):
        info = self.app.save_upload("../../etc/passwd", "../x", io.BytesIO(b"abc"), 3)
        self.assertTrue((self.app.workspace / info["path"]).resolve().is_relative_to(self.app.uploads))

    def test_upload_plan_and_media(self):
        for name in ("a.mp4", "b.mp4"):
            code, _ = self.req(f"/api/upload?name={name}&dir=vids", b"video-" + name.encode(), raw=True)
            self.assertEqual(code, 200)
        self.req("/api/upload?name=a.txt&dir=vids", "Hola #fyp".encode(), raw=True)
        brief = {"product": {"name": "P", "url": "https://x.test/p"},
                 "kalodata": {"videos_dir": "uploads/vids"},
                 "campaign": {"structure": "abo_1_n_1", "daily_budget": 5, "naming": {"ad": ""}}}
        code, body = self.req("/api/plan", brief)
        self.assertEqual(code, 200, body)
        data = json.loads(body)
        self.assertEqual(len(data["plan"]["adsets"]), 2)
        self.assertEqual(data["total_daily_budget"], 10)
        self.assertEqual(data["creatives"][0]["primary_text"], "Hola")
        self.assertEqual(data["plan"]["adsets"][0]["ads"][0]["name"], "P | V1-a")  # naming vacío -> default

        media = data["creatives"][0]["media_url"]
        code, body = self.req(media, headers={"Range": "bytes=0-4"})
        self.assertEqual((code, body), (206, b"video"))
        # archivos fuera del plan no se sirven
        code, _ = self.req("/media?path=/etc/passwd")
        self.assertEqual(code, 404)

    def test_plan_error_is_400(self):
        code, body = self.req("/api/plan", {"product": {"name": "P"}, "campaign": {"daily_budget": 5}})
        self.assertEqual(code, 400)
        self.assertIn("No hay videos", json.loads(body)["error"])

    def test_rejects_foreign_host(self):
        code, _ = self.req("/api/status", headers={"Host": "evil.example"})
        self.assertEqual(code, 403)

    def test_brief_yaml_roundtrip(self):
        brief = {"product": {"name": "P", "url": ""}, "campaign": {"countries": ["AR"]}, "_base_dir": "/x"}
        code, body = self.req("/api/brief/yaml", brief)
        text = json.loads(body)["yaml"]
        self.assertNotIn("url", text)
        self.assertNotIn("_base_dir", text)
        code, body = self.req("/api/brief/parse", {"text": text})
        self.assertEqual(json.loads(body), {"product": {"name": "P"}, "campaign": {"countries": ["AR"]}})


if __name__ == "__main__":
    unittest.main()
