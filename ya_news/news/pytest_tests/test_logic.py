from http import HTTPStatus
from random import choice

import pytest
from pytest_django.asserts import assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from .conftest import TEXT_COMMENT, NEW_COMMENT_TEXT


def test_anonymous_user_cant_create_comment(client, detail_url):
    comments_count = Comment.objects.count()
    client.post(detail_url, data={'text': TEXT_COMMENT})
    assert Comment.objects.count() == comments_count


def test_user_can_create_comment(admin_user, admin_client, detail_url, news):
    Comment.objects.all().delete()
    response = admin_client.post(detail_url, data={'text': TEXT_COMMENT})
    comment = Comment.objects.get()
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert comment.text == TEXT_COMMENT
    assert comment.news == news
    assert comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, detail_url):
    comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == comments_count
    assertFormError(response, 'form', 'text', WARNING)


@pytest.mark.parametrize('user_fixture, expected_status, should_delete', [
    ('author_client', HTTPStatus.FOUND, False),
    ('reader_client', HTTPStatus.NOT_FOUND, True),
])
def test_comment_deletion(
    delete_url, url_to_comments, user_fixture,
    expected_status, should_delete, request
):
    user = request.getfixturevalue(user_fixture)
    response = user.delete(delete_url)
    assert response.status_code == expected_status
    assert Comment.objects.count() == should_delete
    if not should_delete:
        assert response.url == url_to_comments


@pytest.mark.parametrize('user_fixture, expected_status, should_edit', [
    ('author_client', HTTPStatus.FOUND, True),
    ('reader_client', HTTPStatus.NOT_FOUND, False),
])
def test_comment_editing(
    comment, edit_url, url_to_comments,
    user_fixture, expected_status, should_edit, request
):
    user = request.getfixturevalue(user_fixture)
    response = user.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    touch_comment = Comment.objects.get(pk=comment.pk)
    assert response.status_code == expected_status
    assert touch_comment.author == comment.author
    assert touch_comment.news == comment.news
    if should_edit:
        assert response.url == url_to_comments
        assert touch_comment.text == NEW_COMMENT_TEXT
    else:
        assert touch_comment.text == TEXT_COMMENT
