from sqlalchemy import select, insert
from apps.user.models import User


def test_users(client, db):
    user = User(username='dddfff', email='dmitrii_fuchko@mail.ru', password='12345sdDs#@')
    s = db()
    s.add(user)
    s.commit()
    print(db().query(User).all())

    response = client.get('/users')
    assert response.status_code == 200


def test_users2(client):
    response = client.get('/users')
    assert response.status_code == 200