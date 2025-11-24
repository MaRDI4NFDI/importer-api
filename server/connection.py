from .database import db


def get_engine(mediawiki=False):
    """
    Get SQLAlchemy engine for specified database

    Args:
        mediawiki: Whether to get mediawiki database engine

    Returns:
        SQLAlchemy engine
    """
    if mediawiki:
        return db.get_engine(bind="mediawiki")
    else:
        return db.get_engine()
