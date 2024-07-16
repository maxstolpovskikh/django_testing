from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.non_author = User.objects.create(username='non_author')
        cls.author_client = Client()
        cls.non_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.non_author_client.force_login(cls.non_author)
        cls.note = Note.objects.create(
            title='Test Note',
            text='This is a test note',
            slug='test-note',
            author=cls.author
        )
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.SUCCESS_URL = reverse('notes:success')
        cls.EDIT_URL = reverse('notes:edit', args=[cls.note.slug])
        cls.DELETE_URL = reverse('notes:delete', args=[cls.note.slug])
        cls.LOGIN_URL = reverse('users:login')
