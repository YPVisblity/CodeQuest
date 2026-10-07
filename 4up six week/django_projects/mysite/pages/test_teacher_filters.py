from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Submission


class TeacherFileFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user("filter-teacher", is_staff=True)
        cls.student_a = User.objects.create_user("filter-student-a")
        cls.student_b = User.objects.create_user("filter-student-b")
        cls.group_a = Group.objects.create(name="Class A")
        cls.group_b = Group.objects.create(name="Class B")
        cls.teachers = Group.objects.create(name="Teachers")
        cls.student_a.groups.add(cls.group_a)
        cls.student_b.groups.add(cls.group_b)
        cls.teacher.groups.add(cls.teachers)
        for user, filename in [(cls.student_a, "a.ipynb"), (cls.student_b, "b.py")]:
            Submission.objects.create(user=user, filename=filename, level="test", passed=True)

    def setUp(self):
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        settings_override = override_settings(BASE_DIR=Path(temp_dir.name))
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        submissions = Path(temp_dir.name) / "submissions"
        submissions.mkdir()
        for filename in ["a.ipynb", "b.py", "untracked.txt", "ignored.exe"]:
            (submissions / filename).touch()
        (submissions / "directory.py").mkdir()
        self.client.force_login(self.teacher)
        self.url = reverse("teacher_files")

    def filenames(self, response):
        self.assertEqual(response.status_code, 200)
        return {item["name"] for item in response.context["files"]}

    def test_unfiltered_keeps_all_editable_files(self):
        response = self.client.get(self.url)
        self.assertEqual(self.filenames(response), {"a.ipynb", "b.py", "untracked.txt"})
        self.assertNotIn(self.teachers, response.context["groups"])
        reviewable = {item["name"]: item["can_review"] for item in response.context["files"]}
        self.assertTrue(reviewable["a.ipynb"])
        self.assertFalse(reviewable["b.py"])

    def test_group_limits_files_and_user_choices(self):
        response = self.client.get(self.url, {"group": self.group_a.pk})
        self.assertEqual(self.filenames(response), {"a.ipynb"})
        self.assertEqual(response.context["users"], [self.student_a])
        self.assertContains(response, 'name="group"')
        self.assertContains(response, 'name="user"')
        self.assertNotContains(response, 'data-filename="b.py"')

    def test_user_filter_without_group(self):
        response = self.client.get(self.url, {"user": self.student_b.pk})
        self.assertEqual(self.filenames(response), {"b.py"})

    def test_group_and_user_filter(self):
        response = self.client.get(self.url, {"group": self.group_a.pk, "user": self.student_a.pk})
        self.assertEqual(self.filenames(response), {"a.ipynb"})

    def test_invalid_or_mismatched_filters_are_rejected(self):
        for query in [
            {"group": "invalid"},
            {"group": self.teachers.pk},
            {"user": "invalid"},
            {"group": self.group_a.pk, "user": self.student_b.pk},
        ]:
            with self.subTest(query=query):
                self.assertEqual(self.client.get(self.url, query).status_code, 403)

    def test_empty_group_has_no_files(self):
        group = Group.objects.create(name="Empty class")
        response = self.client.get(self.url, {"group": group.pk})
        self.assertEqual(self.filenames(response), set())

    def test_student_cannot_access_teacher_files(self):
        self.client.force_login(self.student_a)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)
