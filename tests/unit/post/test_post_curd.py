from src.post.services import PostUpdateDto


def test_simple_curd_post(user_service, post_service):
    account = "kybdev1@gmail.com"
    password = "1q2w3e4r1!"
    title = "test title.."
    body = "test body.."

    res = user_service.create_user(account, password)
    tags = ["개발", "공부", "취미"]
    for tag in tags:
        post_service.upsert_tag(tag)

    # create...
    post_id = post_service.create_post(res.user_id, title, body, tags)
    # read
    post = post_service.get_post(post_id)

    assert post.id == post_id
    assert post.title == title
    assert post.body == body
    assert sorted(post.tags) == tags

    changed_title = "changed title..."
    changed_body = "changed body"
    changed_tags = ["공부"]
    # update
    post_service.update_post(PostUpdateDto(
        id=post_id,
        title=changed_title,
        body=changed_body,
        tags=changed_tags
    ))
    post = post_service.get_post(post_id)
    assert post.id == post_id
    assert post.title == changed_title
    assert post.body == changed_body
    assert sorted(post.tags) == sorted(changed_tags)

    # delete