from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from pages import views


class TeacherStudentIdTests(SimpleTestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / '987' / 'chapter-1-level-1-1_answer.ipynb'
        self.path.parent.mkdir()
        self.path.write_text('{}', encoding='utf-8')
        self.teacher = SimpleNamespace(id=123, is_authenticated=True, is_staff=True)

    def test_list_regrade_uses_file_owner_id(self):
        request = RequestFactory().post('/teacher/files/987/answer.ipynb/review/')
        request.user = self.teacher
        with patch.object(views, '_safe_student_file', return_value=self.path), \
             patch.object(views, '_test_code_for_level', return_value='tests'), \
             patch.object(views, 'evaluate_student_file', return_value={'passed': True}) as evaluate:
            response = views.teacher_review_one_file(request, '987/answer.ipynb')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(evaluate.call_args.kwargs['std_id3n'], 987)

    def test_edit_page_regrade_uses_file_owner_id(self):
        request = RequestFactory().post('/teacher/files/987/answer.ipynb/')
        request.user = self.teacher
        with patch.object(views, '_safe_student_file', return_value=self.path), \
             patch.object(views, '_test_code_for_level', return_value='tests'), \
             patch.object(views, 'render', return_value=HttpResponse()), \
             patch.object(views, 'evaluate_student_file', return_value={'passed': True}) as evaluate:
            response = views.teacher_file_edit(request, '987/answer.ipynb')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(evaluate.call_args.kwargs['std_id3n'], 987)

    def test_group_assignment_regrade_uses_student_not_uploader(self):
        submission = SimpleNamespace(
            student_id=987, uploaded_by_id=123, assignment_id=1,
            notebook=SimpleNamespace(path=str(self.path)),
            assignment=SimpleNamespace(test_code='tests', compiled_reference=SimpleNamespace(path='reference.pkl')),
            save=Mock(),
        )
        with patch.object(views, 'evaluate_student_file', return_value={'passed': True}) as evaluate:
            views.grade_submission(submission)
        self.assertEqual(evaluate.call_args.kwargs['std_id3n'], 987)
        self.assertTrue(submission.result['passed'])


class IdReferencePortabilityTests(SimpleTestCase):
    def test_pickled_reference_has_no_bytecode(self):
        # pkl 裡若存了 closure 的 bytecode，換 Python 版本載入就會 SystemError: unknown opcode
        import dill
        from pages.id_reference import ExpectedTransform, build_reference

        test_source = (
            "user_id = int(std_id3n)\n"
            "_id_observations = {'double': ('demo', 'double', user_id, double(user_id))}\n"
        )
        reference = build_reference('demo', 'def double(x):\n    return 2 * x\n', test_source)
        raw = dill.dumps(reference)
        self.assertNotIn(b'_create_code', raw)

        transform = dill.loads(raw).annotations[0].value.transforms[-1]
        self.assertIsInstance(transform, ExpectedTransform)
        self.assertEqual(transform(21), ('demo', 'double', 21, 42))
