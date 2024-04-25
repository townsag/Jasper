import os 
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', 
        DATABASE=os.path.join(app.instance_path, "chat_microservice.sqlite")
        )

    # this allows us to load a different configuration at test time
    # the default behavior (loading the instance config) will still work the same
    # in the absence of a test config
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    connect_blueprints_and_resources(app=app)

    from flask_jwt_extended import JWTManager
    # ToDo: store JWT secret key in config file
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
    # ToDo: is this doing anything or can it be removed
    jwt = JWTManager(app)

        # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

def connect_blueprints_and_resources(app):
    from . import db
    db.init_app(app)

    from . import llm
    llm.init_app(app)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import chat
    app.register_blueprint(chat.chat_bp)