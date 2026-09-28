from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class SignUpTests(TestCase):
    def test_signup_page(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_signup(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'somepassword123',
            'password2': 'somepassword123',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'newuser')

    def test_login(self):
        User.objects.create_user(username='newuser', password='somepassword123')
        response = self.client.post(reverse('login'), {'username': 'newuser', 'password': 'somepassword123'})
        self.assertRedirects(response, '/polls/')
