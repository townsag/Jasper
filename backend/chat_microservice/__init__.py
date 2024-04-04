import os 
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', 
        DATABASE=os.path.join(app.instance_path, "chat_microservice.sqlite")
        )
    app.config.from_pyfile("config.py", silent=False)
    print(app.config)
    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ToDo: separate out the logic to initialize the the database, blueprints, extentions, etc.
    from . import db
    db.init_app(app)

    from . import llm
    llm.init_app(app)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import chat
    app.register_blueprint(chat.chat_bp)

    from flask_jwt_extended import JWTManager
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
    jwt = JWTManager(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return f'Hello, World! {app.instance_path}'

    return app