from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url):
    client.post(detail_url, data={'text': 'Текст комментария'})
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(client, author, detail_url, news):
    client.force_login(author)
    response = client.post(detail_url, data={'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(client, author, detail_url):
    client.force_login(author)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize('user_fixture, expected_status, should_delete', [
    ('author', HTTPStatus.FOUND, True),
    ('reader', HTTPStatus.NOT_FOUND, False),
])
def test_comment_deletion(
    client, comment, delete_url, url_to_comments,
    user_fixture, expected_status, should_delete, request
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.delete(delete_url)
    assert response.status_code == expected_status
    if should_delete:
        assert response.url == url_to_comments
        assert Comment.objects.count() == 0
    else:
        assert Comment.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize('user_fixture, expected_status, should_edit', [
    ('author', HTTPStatus.FOUND, True),
    ('reader', HTTPStatus.NOT_FOUND, False),
])
def test_comment_editing(
    client, comment, edit_url, url_to_comments,
    user_fixture, expected_status, should_edit, request
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    new_text = 'Обновлённый комментарий'
    response = client.post(edit_url, data={'text': new_text})
    assert response.status_code == expected_status
    comment.refresh_from_db()
    if should_edit:
        assert response.url == url_to_comments
        assert comment.text == new_text
    else:
        assert comment.text == 'Текст комментария'
