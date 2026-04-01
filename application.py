from flask import Flask
from flask_restful import Api

from config import Config
from models import db
from resources.blacklist import BlacklistResource, BlacklistQueryResource
from schemas import ma


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)

    api = Api(app)
    api.add_resource(BlacklistResource, "/blacklists")
    api.add_resource(BlacklistQueryResource, "/blacklists/<string:email>")

    with app.app_context():
        db.create_all()

    return app


application = create_app()

if __name__ == "__main__":
    application.run(debug=False)
