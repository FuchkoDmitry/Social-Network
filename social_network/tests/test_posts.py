import pytest
from sqlalchemy import and_

from apps.post import models
from apps.user import models as u_models


def test_create_post(db, client, active_user_with_post, token):
    data = {
        "title": "post_title",
        "content": "post_content"
    }
    response = client.post('/posts', data=data, headers={"Authorization": f"Bearer {token}"})
    new_post = response.json()

    assert response.status_code == 201
    assert new_post['title'] == data['title']
    assert new_post['content'] == data['content']
    assert new_post['owner_id'] == active_user_with_post.id


def test_get_posts(db, client):
    posts_count = db().query(models.Post).count()

    response = client.get('/posts')

    assert response.status_code == 200
    assert len(response.json()) == posts_count


def test_get_post(db, client):
    post_in_db = db().query(models.Post).first()

    response = client.get(f'/posts/{post_in_db.id}')

    response_json = response.json()

    assert response.status_code == 200
    assert response_json['content'] == post_in_db.content
    assert response_json['title'] == post_in_db.title
    assert response_json['post_owner']['id'] == post_in_db.owner_id


def test_delete_post_not_post_owner(db, client, active_user_post, active_user_without_post, user_without_post_token):

    response = client.delete(
        f'/posts/{active_user_post.id}', headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    post_after_failure_delete = db().query(models.Post).get(active_user_post.id)

    assert response.status_code == 403
    assert response.json()['detail'] == 'Forbidden'
    assert active_user_post.deleted is False
    assert post_after_failure_delete.deleted is False


def test_delete_post_to_unauthorized_user(db, client, active_user_post):
    response = client.delete(
        f'/posts/{active_user_post.id}'
    )

    post_after_failure_delete = db().query(models.Post).get(active_user_post.id)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'
    assert active_user_post.deleted is False
    assert post_after_failure_delete.deleted is False


def test_delete_post(db, client, active_user_post, token):

    response = client.delete(f'/posts/{active_user_post.id}', headers={"Authorization": f"Bearer {token}"})

    post_after_deleted = db().query(models.Post).get(active_user_post.id)

    assert response.status_code == 204
    assert active_user_post.deleted is False
    assert post_after_deleted.deleted is True


def test_partial_update_post(db, client, post_to_update, token):
    data = {
        "title": "update only title"
    }

    response = client.patch(
        f'/posts/{post_to_update.id}', data=data, headers={"Authorization": f"Bearer {token}"}
    )
    response_json = response.json()

    post_after_update = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 200
    assert response_json['title'] == data['title'] == post_after_update.title != post_to_update.title
    assert post_to_update.content == post_after_update.content


def test_update_post(db, client, token, post_to_update):
    data = {
        "title": "updated title",
        "content": "updated content"
    }

    response = client.put(f'posts/{post_to_update.id}', data=data, headers={"Authorization": f"Bearer {token}"})
    response_json = response.json()

    post_after_update = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 200
    assert response_json['title'] == data['title'] == post_after_update.title
    assert response_json['content'] == data['content'] == post_after_update.content
    assert post_to_update.title != post_after_update.title


def test_add_like_to_not_exist_post(db, client, token):

    response = client.post(
        '/posts/999/like', headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Post not found"


def test_add_like_to_own_post(db, client, post_to_update, token):
    likes_before_adding = len(post_to_update.post_likes)

    response = client.post(
        f'/posts/{post_to_update.id}/like', headers={"Authorization": f"Bearer {token}"}
    )

    post_after_try_to_add_like = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 400
    assert likes_before_adding == len(post_after_try_to_add_like.post_likes)
    assert response.json()['detail'] == "Forbidden. It's your post"


def test_add_like_to_post(db, client, post_to_update, user_without_post_token):
    likes_before_adding = len(post_to_update.post_likes)

    response = client.post(
        f'/posts/{post_to_update.id}/like', headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    post_after_like_added = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 201
    assert likes_before_adding + 1 == len(post_after_like_added.post_likes)
    assert response.json()['message'] == 'Success'


def test_add_dislike_to_not_exist_post(db, client, token):

    response = client.post(
        '/posts/999/dislike', headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()['detail'] == "Post not found"


def test_add_dislike_to_own_post(db, client, post_to_update, token):
    dislikes_before_adding = len(post_to_update.post_dislikes)

    response = client.post(
        f'/posts/{post_to_update.id}/dislike', headers={"Authorization": f"Bearer {token}"}
    )

    post_after_try_to_add_dislike = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 400
    assert dislikes_before_adding == len(post_after_try_to_add_dislike.post_dislikes)
    assert response.json()['detail'] == "Forbidden. It's your post"


def test_add_dislike_to_post(db, client, post_to_update, user_without_post_token):
    dislikes_before_adding = len(post_to_update.post_dislikes)

    response = client.post(
        f'/posts/{post_to_update.id}/dislike', headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    post_after_dislike_added = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 201
    assert dislikes_before_adding + 1 == len(post_after_dislike_added.post_dislikes)
    assert response.json()['message'] == 'Success'


def test_post_repost(
        db, client, active_user_with_post, post_to_update,
        active_user_without_post, user_without_post_token
):
    user_reposts_count = len(active_user_without_post.reposts)

    response = client.post(
        f'/posts/{post_to_update.id}/repost', headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    user_reposts_after_repost = db().query(u_models.User).get(active_user_without_post.id)

    assert response.status_code == 201
    assert response.json()['message'] == "Success"
    assert user_reposts_count + 1 == len(user_reposts_after_repost.reposts)


def test_add_comment(db, client, post_to_update, user_without_post_token):
    comments_before_add_new = len(post_to_update.comments)
    new_comment = {
        "content": "comment"
    }

    response = client.post(
        f'/posts/{post_to_update.id}/comment',
        json=new_comment,
        headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    post_after_add_new_comment = db().query(models.Post).get(post_to_update.id)

    assert response.status_code == 201
    assert comments_before_add_new + 1 == len(post_after_add_new_comment.comments)
    assert response.json() == {"success": "Your comment has been added"}


def test_update_comment(db, client, active_user_without_post, user_without_post_token):
    data = {"content": "updated comment"}
    comment_before_update = db().query(models.Comment).filter(
        models.Comment.owner_id == active_user_without_post.id).first()

    response = client.patch(
        f'/comments/{comment_before_update.id}', json=data,
        headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    comment_after_update = db().query(models.Comment).get(comment_before_update.id)

    assert response.status_code == 200
    assert comment_after_update.content == data['content'] != comment_before_update.content


def test_delete_not_own_comment(db, client, active_user_without_post, token):
    comment_to_try_delete = db().query(models.Comment).filter(
        models.Comment.owner_id == active_user_without_post.id).first()

    response = client.put(
        f'/comments/{comment_to_try_delete.id}', headers={"Authorization": f"Bearer {token}"}
    )

    comment_after_trying_to_delete = db().query(models.Comment).get(comment_to_try_delete.id)

    assert response.status_code == 403
    assert comment_to_try_delete.deleted == comment_after_trying_to_delete.deleted == False
    assert response.json() == {'detail': "It's not your comment"}


def test_delete_own_comment(db, client, active_user_without_post, user_without_post_token):
    comments = db().query(models.Comment).filter(
        and_(
            models.Comment.owner_id == active_user_without_post.id,
            models.Comment.deleted == False
        )
    ).all()
    comment_to_delete = comments[0]

    response = client.put(
        f'/comments/{comment_to_delete.id}',
        headers={"Authorization": f"Bearer {user_without_post_token}"}
    )

    comments_count_after_deleted = db().query(models.Comment).filter(
        and_(
            models.Comment.owner_id == active_user_without_post.id,
            models.Comment.deleted == False
        )
    ).count()

    assert response.status_code == 204
    assert response.json() == {"message": "Comment has been deleted"}
    assert comments_count_after_deleted == len(comments) - 1
