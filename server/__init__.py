import os
from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    db_user = os.environ["MYSQL_USER"]
    db_pass = os.environ["MYSQL_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["MYSQL_DATABASE"]

    workers = int(os.getenv("GUNICORN_WORKERS", 4))
    threads = int(os.getenv("GUNICORN_THREADS", 2))

    total_potential = workers * threads
    pool_size = max(5, total_potential // 2)
    max_overflow = pool_size

    app.logger.info(
        f"Configuring DB pools: workers={workers}, threads={threads}, "
        f"pool_size={pool_size}, max_overflow={max_overflow}"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}?charset=utf8mb4"
    )

    # Mediawiki database bind
    app.config["SQLALCHEMY_BINDS"] = {
        "mediawiki": f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/my_wiki?charset=utf8mb4"
    }

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_timeout": 30,
        "echo": False,
        "echo_pool": False,
    }

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from .database import init_db

    init_db(app)

    register_routes(app)
    register_error_handlers(app)

    return app


def register_routes(app):
    """Register all application routes"""
    from .mapping import get_mapping
    from .search import search_items, search_properties

    @app.route("/health")
    def health_check():
        """
        Health check endpoint for load balancers and monitoring
        Returns 200 if app and database are healthy
        """
        try:
            from .database import db

            # Quick ping to verify DB connectivity
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))

            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({"status": "unhealthy", "error": str(e)}), 503

    @app.route("/items/<item_id>/mapping")
    def get_item_mapping(item_id):
        """Get mapping for an item by ID"""
        try:
            mapping = get_mapping(item_id)
            if mapping:
                return jsonify(mapping)
            return jsonify({"error": "Item not found"}), 404
        except Exception as e:
            app.logger.error(f"Error getting item mapping: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/properties/<property_id>/mapping")
    def get_property_mapping(property_id):
        """Get mapping for a property by ID"""
        try:
            mapping = get_mapping(property_id)
            if mapping:
                return jsonify(mapping)
            return jsonify({"error": "Property not found"}), 404
        except Exception as e:
            app.logger.error(f"Error getting property mapping: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/search/items/<path:label>")
    def get_items(label):
        """Search for items by label"""
        try:
            results = search_items(label)
            return jsonify(results)
        except Exception as e:
            app.logger.error(f"Error searching items: {e}")
            return jsonify({"error": "Internal server error"}), 500

    @app.route("/search/properties/<path:label>")
    def get_properties(label):
        """Search for properties by label"""
        try:
            results = search_properties(label)
            return jsonify(results)
        except Exception as e:
            app.logger.error(f"Error searching properties: {e}")
            return jsonify({"error": "Internal server error"}), 500


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(f"Unhandled Exception: {error}")
        return jsonify({"error": "An unexpected error occurred"}), 500
