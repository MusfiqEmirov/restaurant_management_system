from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class MixinTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.obj = DummyModel.objects.create(name="Test", created_by=self.user, updated_by=self.user)

    def test_soft_delete(self):
        self.obj.delete()
        self.assertTrue(self.obj.is_deleted)
        self.assertIsNotNone(self.obj.deleted_at)

    def test_restore(self):
        self.obj.delete()
        self.obj.restore()
        self.assertFalse(self.obj.is_deleted)
        self.assertIsNone(self.obj.deleted_at)

    def test_audit_fields(self):
        self.assertEqual(self.obj.created_by, self.user)
        self.assertEqual(self.obj.updated_by, self.user)

