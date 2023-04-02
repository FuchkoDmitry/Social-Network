import pytest

from apps.user.models import User


def test_user_registration(client, db):
    data = {
        "username": "test_user",
        "email": "dmitrii_fuchko@mail.ru",
        "password": "DfDfg#453!",
        "confirm_password": "DfDfg#453!",
    }

    response = client.post('/users', data=data)

    registered_user = db().query(User).filter(User.email == data['email']).first()

    assert response.status_code == 201
    assert registered_user.email == data['email']
    assert response.json() == {"message": f"Congratulations! Your registration has been successfully. "
                                          f"Activation link has been sent to {data['email']}"
                               }


def test_activate_user(client, db, registered_user):
    user = db().query(User).get(registered_user.id)

    response = client.get(f'/users/activate/?uuid={user.uuid_to_activate}')

    user_after_activate = db().query(User).get(registered_user.id)

    assert user.is_active is False
    assert response.status_code == 200
    assert response.json() == {
        f"message":
            f'User "{registered_user.username}" with email "{registered_user.email} activated successfully"'
    }
    assert user_after_activate.is_active is True


def test_user_login(client, db, active_user_with_post):
    data = {
        "username": active_user_with_post.username,
        "password": 'QwerTy1234#$'
    }
    response = client.post('/users/login', data=data)

    token = response.json()

    assert response.status_code == 200
    assert token['token_type'] == "Bearer"
    assert token.get('access_token') is not None


def test_users_me(client, db, token, active_user_with_post):

    response = client.get('/users/me/', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()['username'] == active_user_with_post.username


def test_get_users(client, db):
    users_in_db = db().query(User).all()

    response = client.get("users/")

    assert response.status_code == 200
    assert len(response.json()) == len(users_in_db)


def test_get_user(client, db, registered_user):
    response = client.get(f'/users/{registered_user.id}')

    response_user = response.json()

    assert response.status_code == 200
    assert response_user['username'] == registered_user.username
    assert response_user['email'] == registered_user.email
