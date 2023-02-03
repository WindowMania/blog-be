import random
from src.post.services import PostService


def create_post(user_id, post_service: PostService, post_size: int = 10):
    tags = ["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9"]
    for tag in tags:
        post_service.upsert_tag(tag)
    ret = []
    for i in range(post_size):
        sample_tags = random.sample(tags, random.randrange(0, len(tags)))
        title = "title_" + str(i)
        body = "body_" + str(i)
        post_id = post_service.create_post(user_id, title, body, sample_tags)
        ret.append(post_service.get_post(post_id))
    return ret, tags
