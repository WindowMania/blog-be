def test_create_post(user_service, post_service):
    # res = user_service.create_user("kybdev1@gmail.com", "1q2w3e4r1!")
    tags = ["개발", "공부", "취미"]
    for tag in tags:
        post_service.upsert_tag(tag)

    post_id = post_service.create_post("4c0e684b76b446d996690e479c481903", "테스트,,", "테스트..", tags)
    print(post_id)
