"""Integration checks for the generated learning reader and local execution boundary."""
import json
import re
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .web_catalog import collect, build
from .web_server import LearningServer


class WebLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build()
        cls.server = LearningServer(("127.0.0.1", 0), cls.catalog)
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def post(self, body, token=None, origin=None):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-MiniAgent-Token"] = token
        if origin:
            headers["Origin"] = origin
        return urlopen(Request(self.base + "/api/run", json.dumps(body).encode(), headers), timeout=5)

    def test_all_course_content_is_reachable(self):
        lessons = {l["id"]: l for l in self.catalog["lessons"]}
        self.assertEqual(len(self.catalog["stages"]), 9)
        self.assertEqual(len(self.catalog["extensions"]), 4)
        self.assertEqual(sum(s["task_count"] for s in self.catalog["stages"]), 50)
        self.assertEqual(sum(l["runnable"] for l in lessons.values()), 14)
        for stage in self.catalog["stages"]:
            for key in ("lesson", "prerequisite", "tasks"):
                self.assertIn(stage[key], lessons)
        for extension in self.catalog["extensions"]:
            self.assertEqual(lessons[extension["lesson"]]["track"], "extension")

    def test_static_content_and_download(self):
        self.assertEqual(urlopen(self.base + "/", timeout=5).status, 200)
        result = json.load(urlopen(self.base + "/files/step0/stage0-learning.ipynb", timeout=5))
        self.assertEqual(result["nbformat"], 4)

    def test_continuous_lessons_keep_source_code_and_course_tasks(self):
        lessons = {lesson["id"]: lesson for lesson in self.catalog["lessons"]}
        for stage in self.catalog["stages"]:
            reading = stage["reading"]
            self.assertTrue(reading["question"])
            self.assertTrue(reading["thinking"])
            self.assertGreaterEqual(len(reading["units"]), 3)
            nodes = list(reading["setup"])
            for unit in reading["units"]:
                nodes.extend(unit["before"] + unit["body"] + unit["after"])
            # A merged reader must not drop, duplicate or reorder executable cells.
            indices = [node["cell"] for node in nodes
                       if node["lesson"] == stage["lesson"] and "cell" in node
                       and lessons[node["lesson"]]["cells"][node["cell"]]["type"] == "code"]
            expected = [i for i, cell in enumerate(lessons[stage["lesson"]]["cells"])
                        if cell["type"] == "code"]
            self.assertEqual(indices, expected)
            for node in nodes:
                self.assertIn(node["lesson"], lessons)
                if "cell" in node:
                    self.assertLess(node["cell"], len(lessons[node["lesson"]]["cells"]))
            self.assertEqual(reading["assessment"]["lesson"], stage["tasks"])
            tasks = re.findall(r"^\| (S\d+\.\d+) \|", reading["assessment"]["source"], re.M)
            self.assertEqual(len(tasks), stage["task_count"])
        stage1 = self.catalog["stages"][1]["reading"]
        self.assertTrue(any("dispatcher（工具分发器）" in node.get("source", "")
                            for node in stage1["units"][1]["before"]))
        stage2 = self.catalog["stages"][2]["reading"]
        full = "step2/step2_stage2_diagnostics_fixed.ipynb"
        self.assertEqual([node["cell"] for node in stage2["units"][-1]["body"] if "cell" in node],
                         list(range(len(lessons[full]["cells"]))))

    def test_cross_origin_execution_is_denied(self):
        for token, origin in [(None, None), (self.server.token, "https://other.example")]:
            with self.assertRaises(HTTPError) as error:
                self.post({"lesson": "step0/stage0-learning.ipynb"}, token, origin)
            self.assertEqual(error.exception.code, 403)

    def test_arbitrary_paths_and_code_are_denied(self):
        for lesson in ["../README.md", "learning/runtime.py", "print('arbitrary')", "step1/codex_sdk/test_codex.ipynb"]:
            with self.assertRaises(HTTPError) as error:
                self.post({"lesson": lesson}, self.server.token, self.base)
            self.assertEqual(error.exception.code, 400)
        for body in [{"lesson": "step0/stage0-learning.ipynb", "mode": "practice"},
                     {"lesson": "step1/stage1-learning.ipynb", "mode": "arbitrary-shell"}]:
            with self.assertRaises(HTTPError) as error:
                self.post(body, self.server.token, self.base)
            self.assertEqual(error.exception.code, 400)

    def test_host_rebinding_and_directory_listing_are_denied(self):
        request = Request(self.base + "/api/status", headers={"Host": "other.example:" + str(self.server.server_port)})
        with self.assertRaises(HTTPError) as error:
            urlopen(request, timeout=5)
        self.assertEqual(error.exception.code, 403)
        with self.assertRaises(HTTPError):
            urlopen(self.base + "/files/", timeout=5)


if __name__ == "__main__":
    unittest.main()
