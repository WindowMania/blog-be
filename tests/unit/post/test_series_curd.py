from tests.dummy.user import create_test_user
from tests.dummy.post import create_post


def test_series_create(series_service, post_service, user_service, user_auth_service, user_email_service):
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
    assert found_series.title == title
    assert found_series.body == body
    assert all(
        a == b for a, b in zip(post_id_list, [post_id for order, post_id in found_series.get_post_id_and_order()])
    )