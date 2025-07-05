from flask import Flask
from .routes.main import main_bp
from .config import Config
from .extensions import mongo
from .routes.webhook import webhook_bp
import logging
from .extensions import limiter
from flask_cors import CORS

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config.from_pyfile('config.py', silent=True)  # from /instance/config.py

    mongo.init_app(app)  # Initialize Mongo

    app.register_blueprint(webhook_bp)

    app.register_blueprint(main_bp)

    app.logger.setLevel(logging.INFO)

    limiter.init_app(app)

    CORS(app)  # ⚠️ For production, restrict to your frontend origin

    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    return app
