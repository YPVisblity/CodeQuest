import dill
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import nbformat
from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .views import compile_notebook_reference
from .models import GroupAssignment, AssignmentSubmission


class GroupAssignmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user("assignment-teacher", is_staff=True)
        cls.student = User.objects.create_user("assignment-student")
        cls.other = User.objects.create_user("assignment-other")
        cls.outsider = User.objects.create_user("assignment-outsider")
        cls.group = Group.objects.create(name="Assignment class")
        cls.group.user_set.add(cls.student, cls.other)

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        # Field storage is initialized when models load, so change the actual instances.
        for model, fields in [(GroupAssignment, ["prompt_file", "reference_file", "compiled_reference"]),
                              (AssignmentSubmission, ["notebook"])]:
            for name in fields:
                storage = model._meta.get_field(name).storage
                location = patch.object(storage, "_location", self.folder.name)
                location.start()
                self.addCleanup(location.stop)
                storage.__dict__.pop("location", None)
                storage.__dict__.pop("base_location", None)
                self.addCleanup(lambda s=storage: (s.__dict__.pop("location", None), s.__dict__.pop("base_location", None)))
        self.client.force_login(self.teacher)
        self.list_url = reverse("group_assignments", args=[self.group.pk])
        import pybryt
        reference = pybryt.ReferenceImplementation("fixture", [pybryt.Value(156)])
        self.compiler = patch("pages.views.compile_notebook_reference", return_value=dill.dumps(reference))
        self.compiler.start()
        self.addCleanup(self.compiler.stop)

    def reference_upload(self, content=None):
        code = content if content is not None else "import pybryt\ndef value(x, y):\n    return x * y\npybryt.Value(value(26, 6), name='multiplication')"
        nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(code)])
        return SimpleUploadedFile("reference.ipynb", nbformat.writes(nb).encode())

    def notebook(self, code="def value(x, y):\n    return x * y"):
        nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(code + "\nresult = value(26, 6)")])
        return SimpleUploadedFile("student.ipynb", nbformat.writes(nb).encode())

    def create_assignment(self):
        response = self.client.post(self.list_url, {
            "title": "乘法作業", "description": "請撰寫 value(x, y)。",
            "reference_file": self.reference_upload(),
            "prompt_file": SimpleUploadedFile("question.md", b"Implement value(x, y)."),
        })
        self.assertEqual(response.status_code, 302)
        return GroupAssignment.objects.get()

    def test_create_assignment_builds_private_reference_and_renders(self):
        assignment = self.create_assignment()
        self.assertEqual(assignment.group, self.group)
        self.assertEqual(assignment.created_by, self.teacher)
        self.assertEqual(assignment.test_code, "")
        self.assertNotIn("test_file", self.client.get(self.list_url).context["form"].fields)
        self.assertTrue(Path(assignment.compiled_reference.path).exists())
        response = self.client.get(reverse("group_assignment_detail", args=[assignment.pk]))
        self.assertContains(response, "代學生上傳並批改")
        self.assertContains(response, "下載題目附件")

    def test_bad_reference_does_not_publish_or_save_files(self):
        for upload in [SimpleUploadedFile("bad.pkl", b"pickle"),
                       SimpleUploadedFile("bad.ipynb", b"{}"),
                       SimpleUploadedFile("old.json", b'{}'),
                       SimpleUploadedFile("bad.json", b"not json")]:
            response = self.client.post(self.list_url, {"title": "Bad", "description": "Q", "reference_file": upload})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        self.assertFalse(GroupAssignment.objects.exists())
        self.assertEqual(list(Path(self.folder.name).iterdir()), [])

    @patch("pages.views.evaluate_student_file")
    def test_teacher_uploads_for_member_and_can_regrade(self, evaluate):
        assignment = self.create_assignment()
        evaluate.return_value = {"passed": True, "messages": "OK", "feedback": []}
        url = reverse("group_assignment_detail", args=[assignment.pk])
        response = self.client.post(url, {"student": self.student.pk, "notebook": self.notebook()})
        self.assertEqual(response.status_code, 302)
        submission = AssignmentSubmission.objects.get()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.uploaded_by, self.teacher)
        self.assertTrue(submission.result["passed"])
        self.assertEqual(evaluate.call_args.kwargs["reference_path"], assignment.compiled_reference.path)
        self.assertEqual(evaluate.call_args.kwargs["test_code"], assignment.test_code)
        self.client.post(url, {"action": "regrade", "submission": submission.pk})
        self.assertEqual(evaluate.call_count, 2)

    @patch("pages.views.evaluate_student_file")
    def test_student_upload_is_self_only_and_results_are_private(self, evaluate):
        assignment = self.create_assignment()
        evaluate.return_value = {"passed": False, "messages": "NOT OK", "feedback": []}
        self.client.force_login(self.student)
        url = reverse("group_assignment_detail", args=[assignment.pk])
        self.client.post(url, {"student": self.other.pk, "notebook": self.notebook()})
        submission = AssignmentSubmission.objects.get()
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.uploaded_by, self.student)
        self.assertEqual(self.client.post(url, {"action": "regrade", "submission": submission.pk}).status_code, 403)
        self.client.force_login(self.other)
        response = self.client.get(url)
        self.assertEqual(list(response.context["submissions"]), [])
        self.assertEqual(self.client.get(reverse("assignment_submission_download", args=[submission.pk])).status_code, 403)

    def test_teacher_cannot_upload_for_nonmember(self):
        assignment = self.create_assignment()
        response = self.client.post(reverse("group_assignment_detail", args=[assignment.pk]),
                                    {"student": self.outsider.pk, "notebook": self.notebook()})
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_student_cannot_create_and_outsider_cannot_access(self):
        assignment = self.create_assignment()
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(self.list_url, {}).status_code, 403)
        reference_url = reverse("assignment_download", args=[assignment.pk, "reference"])
        self.assertEqual(self.client.get(reference_url).status_code, 403)
        prompt_url = reverse("assignment_download", args=[assignment.pk, "prompt"])
        response = self.client.get(prompt_url)
        self.assertEqual(response.status_code, 200)
        response.close()
        self.client.force_login(self.outsider)
        for url in [self.list_url, reverse("group_assignment_detail", args=[assignment.pk]), prompt_url, reference_url]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(list(self.client.get(reverse("assignment_groups")).context["groups"]), [])

    @patch("pages.views.evaluate_student_file", side_effect=RuntimeError("kernel unavailable"))
    def test_grading_error_keeps_submission_for_retry(self, evaluate):
        assignment = self.create_assignment()
        response = self.client.post(reverse("group_assignment_detail", args=[assignment.pk]),
                                    {"student": self.student.pk, "notebook": self.notebook()})
        self.assertEqual(response.status_code, 302)
        submission = AssignmentSubmission.objects.get()
        self.assertIsNone(submission.result["passed"])
        self.assertIn("重新批改", submission.result["messages"])
        self.assertTrue(Path(submission.notebook.path).exists())

    def test_invalid_notebook_rejected(self):
        assignment = self.create_assignment()
        response = self.client.post(reverse("group_assignment_detail", args=[assignment.pk]),
                                    {"student": self.student.pk, "notebook": SimpleUploadedFile("bad.ipynb", b"{}")})
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_real_pybryt_reference_distinguishes_memory_footprints(self):
        from pybryt.execution import MemoryFootprint
        import pybryt
        reference = pybryt.ReferenceImplementation("memory-check", [pybryt.Value(156)])
        correct = MemoryFootprint()
        correct.add_value(156)
        wrong = MemoryFootprint()
        wrong.add_value(999)
        self.assertTrue(reference.run(correct).correct)
        self.assertFalse(reference.run(wrong).correct)

    def test_real_notebook_upload_and_grading(self):
        self.compiler.stop()
        assignment = self.create_assignment()
        url = reverse("group_assignment_detail", args=[assignment.pk])
        for code, expected in [("def value(x, y):\n    return x * y", True),
                               ("def value(x, y):\n    return -999", False)]:
            with self.subTest(expected=expected):
                response = self.client.post(url, {"student": self.student.pk, "notebook": self.notebook(code)})
                self.assertEqual(response.status_code, 302)
                submission = AssignmentSubmission.objects.latest("pk")
                self.assertIs(submission.result["passed"], expected, submission.result)
                self.assertTrue(submission.result["feedback"])
        self.assertEqual(AssignmentSubmission.objects.count(), 2)

    def test_compile_error_is_shown_without_publishing(self):
        with patch("pages.views.compile_notebook_reference", side_effect=ValueError("轉檔失敗：沒有檢查點")):
            response = self.client.post(self.list_url, {"title": "Bad", "description": "Q", "reference_file": self.reference_upload()})
        self.assertContains(response, "沒有檢查點")
        self.assertFalse(GroupAssignment.objects.exists())

    def test_reference_example_is_valid_notebook(self):
        response = self.client.get(reverse("assignment_reference_example"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("reference-example.ipynb", response["Content-Disposition"])
        nb = nbformat.reads(response.content.decode(), as_version=4)
        nbformat.validate(nb)
        self.assertIn("pybryt.Value", nb.cells[-1].source)

    def test_reference_compile_timeout(self):
        with patch("pages.views.subprocess.run", side_effect=subprocess.TimeoutExpired("compile", 120)):
            with self.assertRaisesMessage(ValueError, "120 秒"):
                compile_notebook_reference(self.reference_upload())
