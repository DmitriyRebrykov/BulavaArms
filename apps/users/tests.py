from django.test import TestCase

class UserTests(TestCase):
    def test_user_creation(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        self.assertEqual(user.username, 'testuser')


    def test_user_authentication(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        login=self.client.login(username='testuser', password='testpass')
        self.assertTrue(login)

    def test_user_profile(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        profile=Profile.objects.create(user=user, bio='Test bio')
        self.assertEqual(profile.bio, 'Test bio')

    def test_user_permissions(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        user.user_permissions.add(permission)
        self.assertTrue(user.has_perm('app_label.permission_codename'))

    def test_user_deletion(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        user.delete()
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_user_update(self):
        user=User.objects.create_user(username='testuser', password='testpass')
        user.username='updateduser'
        user.save()
        self.assertEqual(user.username, 'updateduser')

    def test_user_list(self):
        User.objects.create_user(username='testuser1', password='testpass')
        User.objects.create_user(username='testuser2', password='testpass')
        users=User.objects.all()
        self.assertEqual(users.count(), 2)
        


        