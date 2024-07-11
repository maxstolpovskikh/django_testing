from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNotesPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.non_author = User.objects.create(username='non_author')
        cls.note = Note.objects.create(
            title='title',
            text='text_note',
            author=cls.author
        )
        cls.LIST_URL = reverse('notes:list')
        cls.ADD_URL = reverse('notes:add')
        cls.EDIT_URL = reverse('notes:edit', args=[cls.note.slug])

    def test_note_visibility_for_users(self):
        test_cases = [
            (self.author, 1, True),
            (self.non_author, 0, False),
        ]
        for user, expected_count, should_contain in test_cases:
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertEqual(object_list.count(), expected_count)
                self.assertEqual(self.note in object_list, should_contain)

    def test_form_presence_on_pages(self):
        self.client.force_login(self.author)
        for url in [self.ADD_URL, self.EDIT_URL]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
