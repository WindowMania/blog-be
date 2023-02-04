import random

import pytest

from tests.dummy.user import create_test_user
from tests.dummy.post import create_post
from src.post.services import NotFoundSeries, SeriesUpdateDto


def test_series_curd(series_service, post_service, user_service, user_auth_service, user_email_service):
    created_user = create_test_user(user_service, user_email_service, user_auth_service)
    posts, tags = create_post(created_user.user_id, post_service)

    title = "test"
    body = "test"
    post_id_list = [p.id for p in posts]

    series_id = series_service.create_series(
        user_id=created_user.user_id,
        title=title,
        body=body,
        post_id_list=post_id_list
    )
    found_series = series_service.find_series(series_id=series_id)
    # create and find
    assert found_series.title == title
    assert found_series.body == body
    assert all(
        a == b for a, b in zip(post_id_list, [post_id for order, post_id in found_series.get_post_id_and_order()])
    )

    changed_title = "changed_title"
    changed_body = "changed_body"

    post_order_list = [i for i in range(len(posts))]
    random.shuffle(post_order_list)
    series_post_list = found_series.series_post_list
    post_order_dict = {}
    for i in range(len(series_post_list)):
        series_post_list[i].set_order_number(post_order_list[i])
        post_order_dict[series_post_list[i].post_id] = post_order_list[i]

    # update
    series_service.update_series(SeriesUpdateDto(
        id=series_id,
        title=changed_title,
        body=changed_body,
        series_post_list=series_post_list
    ))
    found_series = series_service.find_series(series_id=series_id)
    assert found_series.title == changed_title
    assert found_series.body == changed_body
    assert post_order_dict == {
        series_post.post_id: series_post.order_number
        for series_post in found_series.series_post_list
    }

    # remove
    series_service.remove_series(series_id)
    with pytest.raises(NotFoundSeries):
        found_series = series_service.find_series(series_id=series_id)


def test_series_listing(user_service, user_email_service, user_auth_service, series_service):
    created_user = create_test_user(user_service, user_email_service, user_auth_service)

    for i in range(17):
        series_service.create_series(user_id=created_user.user_id,
                                     title="title_" + str(i),
                                     body="body_" + str(i)
                                     )
    ret = series_service.get_list(perPage=10, page=1)
    assert len(ret) == 10
    ret = series_service.get_list(page=2, perPage=10)
    assert len(ret) == 7


def test_series_with_post(user_service, user_email_service, user_auth_service, post_service, series_service):
    created_user = create_test_user(user_service, user_email_service, user_auth_service)
    posts, tags = create_post(created_user.user_id, post_service)
    title = "test"
    body = "test"
    post_id_list = [p.id for p in posts]

    series_id = series_service.create_series(
        user_id=created_user.user_id,
        title=title,
        body=body,
        post_id_list=post_id_list
    )
    found_series = series_service.get_series_with_post(series_id)
    found_post_list = [sp.post for sp in found_series.series_post_list]
    found_post_id_dict = {
        fp.id: [fp.title, fp.body, fp.tags] for fp in found_post_list
    }
    for post in posts:
        assert post.title == found_post_id_dict[post.id][0]
        assert post.body == found_post_id_dict[post.id][1]
        post.tags.sort()
        found_post_id_dict[post.id][2].sort()
        assert all(a == b for a, b in zip(post.tags, found_post_id_dict[post.id][2]))
