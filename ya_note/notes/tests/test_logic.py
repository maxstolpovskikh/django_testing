from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_lib import TestNote


class TestNoteCreation(TestNote):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'New Test Note',
            'text': 'This is a new test note',
            'slug': 'new-test-note'
        }

    def test_user_can_create_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        expected_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        notes_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertFormError(
            response, 'form', 'slug', self.note.slug + WARNING
        )

    def test_empty_slug(self):
        notes = Note.objects.all()
        notes.delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(self.ADD_URL, data=form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(Note.objects.get().slug, slugify(form_data['title']))

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.EDIT_URL, self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        response = self.non_author_client.post(self.EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_delete_note(self):
        notes_count = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_other_user_cant_delete_note(self):
        notes_count = Note.objects.count()
        response = self.non_author_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
