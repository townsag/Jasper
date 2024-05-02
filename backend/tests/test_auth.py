import pytest
import json
from chat_microservice.db import get_db

def test_register(client, app):
    response = client.post(
        "/auth/register", 
        data=json.dumps({"username":"a", "password":"a"}), 
        content_type="application/json"
    )
    # check that the request was successful
    assert response.status_code == 200
    # check that the response contains a JWT
    response_json_str = response.get_data(as_text=True)
    response_data_dict = json.loads(response_json_str)
    assert "access_token" in response_data_dict

    with app.app_context():
        db = get_db()
        assert db.execute("SELECT * FROM user WHERE username='a'").fetchone() is not None


@pytest.mark.parametrize(
        ('username', 'password', 'message'),
        (
            ("", "asdf", "username"),
            ("test", "", "password"),
            ("asdf", "asdf", "unavailable")
        )
)
def test_register_validate_inputs(client, username, password, message):
    response = client.post(
        "/auth/register",
        data=json.dumps({"username":username, "password":password}),
        content_type="application/json"
    )
    assert message in response.get_data(as_text=True)

def test_whoami(client):
    response_register = client.post(
        "/auth/register",
        data=json.dumps({"username":"test", "password":"test"}),
        headers={
            "Content-Type":"application/json"
        }
    )
    jwt_str = json.loads(response_register.get_data(as_text=True)).get("access_token", None)
    response_whoami = client.get(
        "/auth/whoami",
        headers={
            "Authorization":f"Bearer {jwt_str}"
        }
    )
    assert response_whoami.status_code == 200
    assert "test" in response_whoami.get_data(as_text=True)

def test_whoami_unauthenticated(client):
    response_whoami = client.get("/auth/whoami")
    assert response_whoami.status_code == 401

# ToDo: should send a msg in the respone to the get request even on a successful login
def test_login(client, auth):
    response_login = auth.login()
    assert response_login.status_code == 200

    jwt_str = json.loads(response_login.get_data(as_text=True)).get("access_token", None)
    assert jwt_str is not None

    response_who_am_i = client.get(
        "/auth/whoami", 
        headers={
            "Authorization":f"Bearer {jwt_str}"
        }
    )
    assert response_who_am_i.status_code == 200
    assert "asdf" == json.loads(response_who_am_i.get_data(as_text=True)).get("username", None)

@pytest.mark.parametrize(
    ("username", "password", "message", "code"),
    (
        ("incorrect", "asdf", "no user with this username", 401),
        ("asdf", "incorrect", "username or password incorrect", 401),
        ("", "asdf", "username", 400),
        ("asdf", "", "password", 400)
    )
)
def test_login_validate_input(auth, username, password, message, code):
    response_login = auth.login(username=username, password=password)
    assert response_login.status_code == code
    assert message in json.loads(response_login.get_data(as_text=True)).get("msg")