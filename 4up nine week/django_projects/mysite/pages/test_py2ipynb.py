import io
import json
import zipfile
from urllib.parse import quote

import nbformat
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .py2ipynb import build_notebook, decode_source, natural_key, source_to_cells


def py_file(name, text, encoding="utf-8"):
    return SimpleUploadedFile(name, text.encode(encoding), content_type="text/x-python")


class SourceToCellsTests(TestCase):
    def test_no_marker_is_one_code_cell(self):
        cells = source_to_cells("x = 1\nprint(x)\n")
        self.assertEqual([c.cell_type for c in cells], ["code"])
        self.assertEqual(cells[0].source, "x = 1\nprint(x)")

    def test_percent_markers_split_cells(self):
        src = "import pybryt\n# %%\nx = 1\n#%% 第三格\ny = 2\n"
        self.assertEqual([c.source for c in source_to_cells(src)], ["import pybryt", "x = 1", "y = 2"])

    def test_markdown_cell(self):
        src = "# %% [markdown]\n# # 標題\n# 說明文字\n# %%\nx = 1\n"
        cells = source_to_cells(src)
        self.assertEqual([c.cell_type for c in cells], ["markdown", "code"])
        self.assertEqual(cells[0].source, "# 標題\n說明文字")

    def test_crlf_and_empty_cells(self):
        cells = source_to_cells("# %%\r\n\r\n# %%\r\nx = 1\r\n")
        self.assertEqual([c.source for c in cells], ["x = 1"])

    def test_natural_key(self):
        names = ["10_c.py", "2_b.py", "1_a.py", "B.py", "a.py", "x²1.py"]
        self.assertEqual(sorted(names, key=natural_key), ["1_a.py", "2_b.py", "10_c.py", "a.py", "B.py", "x²1.py"])

    def test_decode_source(self):
        self.assertEqual(decode_source("中文".encode("utf-8-sig")), "中文")
        self.assertEqual(decode_source("中文".encode("cp950")), "中文")

    def test_build_notebook_with_label(self):
        nb = build_notebook([("a.py", "x = 1"), ("b.py", "y = 2")], label=True)
        self.assertEqual([c.source for c in nb.cells], ["### a.py", "x = 1", "### b.py", "y = 2"])
        nbformat.validate(nb)


class PyToIpynbViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user("py2nb-student", password="pw")

    def setUp(self):
        self.url = reverse("py_to_ipynb")
        self.client.force_login(self.student)

    def read_notebook(self, response):
        return nbformat.reads(b"".join(response.streaming_content).decode("utf-8"), as_version=4)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, {"files": [py_file("a.py", "x = 1")]})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_student_can_convert_single_file(self):
        response = self.client.post(self.url, {"files": [py_file("hello.py", "print('hi')")]})
        self.assertEqual(response.status_code, 200)
        self.assertIn('filename="hello.ipynb"', response["Content-Disposition"])
        nb = self.read_notebook(response)
        self.assertEqual([c.source for c in nb.cells], ["print('hi')"])

    def test_merge_sorted_by_number_in_filename(self):
        files = [py_file("10_c.py", "c = 3"), py_file("2_b.py", "b = 2"), py_file("1_a.py", "a = 1")]
        response = self.client.post(self.url, {"files": files, "mode": "merge", "label": "1"})
        self.assertIn('filename="merged.ipynb"', response["Content-Disposition"])
        nb = self.read_notebook(response)
        self.assertEqual([c.source for c in nb.cells],
                         ["### 1_a.py", "a = 1", "### 2_b.py", "b = 2", "### 10_c.py", "c = 3"])

    def test_each_mode_returns_zip(self):
        files = [py_file("a.py", "a = 1"), py_file("解答.py", "# 中文註解\nb = 2", encoding="cp950")]
        response = self.client.post(self.url, {"files": files, "mode": "each"})
        self.assertEqual(response["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(b"".join(response.streaming_content))) as zf:
            self.assertEqual(sorted(zf.namelist()), ["a.ipynb", "解答.ipynb"])
            nb = nbformat.reads(zf.read("解答.ipynb").decode("utf-8"), as_version=4)
        self.assertEqual(nb.cells[0].source, "# 中文註解\nb = 2")

    def test_chinese_filename_download(self):
        response = self.client.post(self.url, {"files": [py_file("1_爬蟲解答.py", "x = 1")]})
        self.assertIn("filename*=utf-8''" + quote("1_爬蟲解答.ipynb"), response["Content-Disposition"])

    def test_rejects_bad_uploads(self):
        cases = [
            ({}, "請選擇至少一個 .py 檔"),
            ({"files": [py_file("a.txt", "x")]}, "不是 .py 檔"),
            ({"files": [py_file("big.py", "x" * (1024 * 1024 + 1))]}, "超過 1MB"),
            ({"files": [py_file(f"{i}.py", "x") for i in range(51)]}, "一次最多 50 個檔案"),
        ]
        for data, message in cases:
            with self.subTest(message=message):
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(message, json.loads(response.content)["error"])

    def test_uploaded_code_is_not_executed(self):
        evil = "raise SystemExit('不應該被執行')\nimport os; os.remove('不存在的檔案')"
        response = self.client.post(self.url, {"files": [py_file("evil.py", evil)]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.read_notebook(response).cells[0].source, evil)

    def test_csrf_enforced(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(self.url, {"files": [py_file("a.py", "x = 1")]})
        self.assertEqual(response.status_code, 403)

    def test_home_shows_button_only_when_logged_in(self):
        self.assertContains(self.client.get(reverse("home")), 'id="pyToIpynbButton"')
        self.client.logout()
        self.assertNotContains(self.client.get(reverse("home")), 'id="pyToIpynbButton"')
