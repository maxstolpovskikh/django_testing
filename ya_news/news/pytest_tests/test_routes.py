from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize('name, args', [
    ('news:home', None),
    ('news:detail', lambda news: (news.id,)),
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None),
])
def test_pages_availability(client, name, args, news):
    url = reverse(name, args=args(news) if callable(args) else args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('user_fixture, expected_status', [
    ('author', HTTPStatus.OK),
    ('reader', HTTPStatus.NOT_FOUND),
])
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_availability_for_comment_edit_and_delete(
    client, comment, user_fixture, expected_status, name, request
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_redirect_for_anonymous_client(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
