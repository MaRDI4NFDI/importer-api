import os
from flask import Flask, jsonify
from .database import db, init_db
from .mapping import get_mapping
from .search import search_items, search_properties


def create_app():
    app = Flask(__name__)

    db_user = os.environ["MYSQL_USER"]
    db_pass = os.environ["MYSQL_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["MYSQL_DATABASE"]

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mariadb+mariadbconnector://{db_user}:{db_pass}@{db_host}/{db_name}"
    )

    # Mediawiki database bind
    app.config["SQLALCHEMY_BINDS"] = {
        "mediawiki": f"mariadb+mariadbconnector://{db_user}:{db_pass}@{db_host}/my_wiki"
    }

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    init_db(app)

    @app.route("/items/<item_id>/mapping")
    def get_item_mapping(item_id):
        mapping = get_mapping(item_id)
        if mapping:
            return jsonify(mapping)
        return jsonify({"error": "Item not found"})

    @app.route("/properties/<property_id>/mapping")
    def get_property_mapping(property_id):
        mapping = get_mapping(property_id)
        if mapping:
            return jsonify(mapping)
        return jsonify({"error": "Property not found"})

    @app.route("/search/items/<path:label>")
    def get_items(label):
        results = search_items(label)
        return jsonify(results)

    @app.route("/search/properties/<path:label>")
    def get_properties(label):
        results = search_properties(label)
        return jsonify(results)


app = create_app()
