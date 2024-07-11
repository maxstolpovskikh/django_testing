from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.non_author = User.objects.create(username='non_author')
        cls.note = Note.objects.create(
            title='title',
            text='text_note',
            author=cls.author)

        cls.public_urls = [
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ]
        cls.authenticated_urls = [
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
        ]
        cls.note_specific_urls = [
            ('notes:edit', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        ]

    def test_pages_availability_for_anonymous_client(self):
        for name, args in self.public_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_user(self):
        self.client.force_login(self.author)
        for name, args in self.authenticated_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in self.authenticated_urls + self.note_specific_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.non_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in self.note_specific_urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
