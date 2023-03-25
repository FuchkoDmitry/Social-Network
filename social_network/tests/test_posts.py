import pytest

from apps.post import models


def test_create_post(db, client, active_user, token):
    data = {
        "title": "post_title",
        "content": "post_content"
    }
    response = client.post('/posts', data=data, headers={"Authorization": f"Bearer {token}"})
    new_post = response.json()

    assert response.status_code == 201
    assert new_post['title'] == data['title']
    assert new_post['content'] == data['content']
    assert new_post['owner_id'] == active_user.id


def test_get_posts(db, client):
    posts_count = db().query(models.Post).count()

    response = client.get('/posts')

    assert response.status_code == 200
    assert len(response.json()) == posts_count
