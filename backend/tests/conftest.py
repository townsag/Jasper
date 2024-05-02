import os
import tempfile
import json

import pytest
from chat_microservice import create_app
from chat_microservice.db import get_db, init_db

from dotenv import load_dotenv
load_dotenv(".env")


# open the data.sql file and read the contents into _data_sql
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING":True,
        "DATABASE":db_path,
        "OPENAI_API_KEY":os.getenv("OPENAI_API_KEY"),
        "COLLECTION_NAME":os.getenv("COLLECTION_NAME")
    })

    # need to use the app context here because init_db() and get_db() need access to the 
    # g (global in application context) variable and that is not automatically available
    # outside of the normal request cycle
    # from documentation: https://flask.palletsprojects.com/en/latest/appcontext/
    # Flask automatically pushes an application context when handling a request. 
    # View functions, error handlers, and other functions that run during a request will 
    # have access to current_app.
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app 

    os.close(db_fd)
    os.unlink(db_path)

# Tests will use the client to make requests to the application without running the server
# pytest will match the name of a fixture function (ex: client) to the argument of a test 
# function. When the test function is called, pytest calls the fixture function and passes
# the result to the test function
@pytest.fixture
def client(app):
    return app.test_client()

# creates a runner that can call the Click commands registered with the application
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, username="asdf", password="asdf"):
        return self._client.post(
            "/auth/login",
            data=json.dumps({"username":username, "password":password}),
            content_type="application/json"
        )
    
    def login_with_jwt(self, username="asdf", password="asdf"):
        response = self._client.post(
            "/auth/login",
            data=json.dumps({"username":username, "password":password}),
            content_type="application/json"
        )
        JWT_str = json.loads(response.get_data(as_text=True)).get("access_token", None)
        return JWT_str, response

    # loggout is done on the client side by deleting the JWT
    # def logout(self):

@pytest.fixture
def auth(client):
    return AuthActions(client)