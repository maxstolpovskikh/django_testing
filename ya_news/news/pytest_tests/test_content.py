import pytest
from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, home_url, news_list):
    news_count = client.get(home_url).context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, news_list):
    news_objects = client.get(home_url).context['object_list']
    all_dates = [news.date for news in news_objects]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, comments):
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize('user_fixture, expected_form', [
    ('author_client', True),
    ('client', False)
])
def test_comment_form_presence(
    detail_url, user_fixture, expected_form, request
):
    user = request.getfixturevalue(user_fixture)
    response = user.get(detail_url)
    assert ('form' in response.context) == expected_form
    if expected_form:
        assert isinstance(response.context['form'], CommentForm)
