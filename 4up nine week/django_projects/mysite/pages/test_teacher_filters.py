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
        # 提交檔存放在 submissions_dir/<使用者 id>/，Submission.filename 也帶著這層資料夾
        cls.file_a = f"{cls.student_a.pk}/a.ipynb"
        cls.file_b = f"{cls.student_b.pk}/b.ipynb"
        for user, filename in [(cls.student_a, cls.file_a), (cls.student_b, cls.file_b)]:
            Submission.objects.create(user=user, filename=filename, level="test", passed=True)

    def setUp(self):
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        settings_override = override_settings(BASE_DIR=Path(temp_dir.name))
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        submissions = Path(temp_dir.name) / "submissions_dir"
        for filename in [self.file_a, self.file_b, "999/untracked.ipynb",
                         f"{self.student_b.pk}/notes.py", "ignored.exe"]:
            path = submissions / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        (submissions / "directory.ipynb").mkdir()
        self.client.force_login(self.teacher)
        self.url = reverse("teacher_files")

    def filenames(self, response):
        self.assertEqual(response.status_code, 200)
        return {item["name"] for item in response.context["files"]}

    def test_unfiltered_lists_all_notebooks(self):
        # 教師介面只列出 .ipynb（.py / .exe / 資料夾都不列）
        response = self.client.get(self.url)
        self.assertEqual(self.filenames(response), {self.file_a, self.file_b, "999/untracked.ipynb"})
        self.assertNotIn(self.teachers, response.context["groups"])
        self.assertTrue(all(item["can_review"] for item in response.context["files"]))

    def test_group_limits_files_and_user_choices(self):
        response = self.client.get(self.url, {"group": self.group_a.pk})
        self.assertEqual(self.filenames(response), {self.file_a})
        self.assertEqual(response.context["users"], [self.student_a])
        self.assertContains(response, 'name="group"')
        self.assertContains(response, 'name="user"')
        self.assertNotContains(response, f'data-filename="{self.file_b}"')

    def test_user_filter_without_group(self):
        response = self.client.get(self.url, {"user": self.student_b.pk})
        self.assertEqual(self.filenames(response), {self.file_b})

    def test_group_and_user_filter(self):
        response = self.client.get(self.url, {"group": self.group_a.pk, "user": self.student_a.pk})
        self.assertEqual(self.filenames(response), {self.file_a})

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
