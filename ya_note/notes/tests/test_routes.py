from http import HTTPStatus

from django.urls import reverse

from .test_logic import TestNote


class TestRoutes(TestNote):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.public_urls = [
            cls.LOGIN_URL,
            reverse('notes:home'),
            reverse('users:logout'),
            reverse('users:signup'),
        ]
        cls.authenticated_urls = [
            cls.ADD_URL,
            cls.LIST_URL,
            cls.SUCCESS_URL,
        ]
        cls.note_specific_urls = [
            cls.EDIT_URL,
            cls.DELETE_URL,
            reverse('notes:detail', args=(cls.note.slug,)),
        ]

    def test_pages_availability_for_anonymous_client(self):
        for url in self.public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_user(self):
        for url in self.authenticated_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        for url in self.authenticated_urls + self.note_specific_urls:
            with self.subTest(url=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                self.assertRedirects(self.client.get(url), redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.non_author_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in self.note_specific_urls:
                with self.subTest(user=user):
                    self.assertEqual(user.get(url).status_code, status)
