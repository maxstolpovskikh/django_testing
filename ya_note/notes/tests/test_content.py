from notes.forms import NoteForm

from .test_logic import TestNote


class TestNotesContent(TestNote):

    def test_note_visibility_for_users(self):
        self.assertTrue(
            self.note in self.author_client.get(
                self.LIST_URL
            ).context['object_list']
        )
        self.assertFalse(
            self.note in self.non_author_client.get(
                self.LIST_URL
            ).context['object_list']
        )

    def test_form_presence_on_pages(self):
        self.client.force_login(self.author)
        for url in [self.ADD_URL, self.EDIT_URL]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
