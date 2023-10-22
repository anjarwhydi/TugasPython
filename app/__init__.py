from flask import Flask, current_app
from flask_restx import Api
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from .config.config import config_dict
from .views.author import author_ns
from .views.book import book_ns
from .views.borrower import borrower_ns
from .views.borrowing import borrowing_ns
from .views.admin import admin_ns
from .views.auth import auth_ns
from .utils import db
from .logs.log import logger


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    api = Api(
        app,
        doc="/",
        title="REST API COURSE ONLINE",
        description="COURSE ONLINE"
    )

    api.add_namespace(admin_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(author_ns)
    api.add_namespace(book_ns)
    api.add_namespace(borrower_ns)
    api.add_namespace(borrowing_ns)

    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    with app.app_context():
        current_app.extensions['bcrypt'] = bcrypt

    logger.debug('Initial run API FLASK')

    return app