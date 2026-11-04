from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class TeacherGroupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user("group-teacher", is_staff=True)
        cls.student = User.objects.create_user("group-student")
        cls.other = User.objects.create_user("other-student")
        cls.group = Group.objects.create(name="Class A")
        cls.teachers = Group.objects.create(name="Teachers")

    def setUp(self):
        self.url = reverse("teacher_groups")
        self.client.force_login(self.teacher)

    def test_create_and_display_group(self):
        response = self.client.post(self.url, {"action": "create", "name": " Class B "}, follow=True)
        self.assertContains(response, "群組已建立")
        self.assertTrue(Group.objects.filter(name="Class B").exists())

    def test_invalid_names(self):
        for name in ["", "   ", "Class A", "class a", "Teachers", "teachers", "x" * 151]:
            with self.subTest(name=name):
                response = self.client.post(self.url, {"action": "create", "name": name})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["group_form"].errors)
        self.assertEqual(Group.objects.count(), 2)

    def test_add_and_remove_preserves_other_memberships(self):
        other_group = Group.objects.create(name="Other class")
        self.student.groups.add(other_group)
        response = self.client.post(self.url, {"action": "add", "group": self.group.pk,
                                              "add-users": [self.student.pk, self.other.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.group.user_set.count(), 2)
        response = self.client.post(self.url, {"action": "remove", "group": self.group.pk,
                                              "remove-users": [self.student.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.student.groups.filter(pk=self.group.pk).exists())
        self.assertTrue(self.student.groups.filter(pk=other_group.pk).exists())
        self.assertTrue(self.group.user_set.filter(pk=self.other.pk).exists())

    def test_invalid_members_are_rejected_atomically(self):
        response = self.client.post(self.url, {"action": "add", "group": self.group.pk,
                                              "add-users": [self.student.pk, 999999]})
        self.assertTrue(response.context["add_form"].errors)
        self.assertEqual(self.group.user_set.count(), 0)

    def test_empty_selection_shows_error(self):
        response = self.client.post(self.url, {"action": "add", "group": self.group.pk})
        self.assertContains(response, "請至少選擇一位使用者")

    def test_permission_group_cannot_be_managed(self):
        for action in ["add", "remove"]:
            response = self.client.post(self.url, {"action": action, "group": self.teachers.pk,
                                                  f"{action}-users": [self.student.pk]})
            self.assertEqual(response.status_code, 404)
        self.assertFalse(self.teachers.user_set.exists())

    def test_student_denied_and_anonymous_redirected(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, {"action": "create", "name": "Forbidden"}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_teacher_role_and_selected_page(self):
        self.student.groups.add(self.teachers)
        self.client.force_login(self.student)
        response = self.client.get(self.url, {"group": self.group.pk})
        self.assertContains(response, "加入勾選的使用者")
        self.assertContains(response, "group-student")
