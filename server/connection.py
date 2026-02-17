import sqlalchemy as sa
from .database import db

_mediawiki_metadata = None


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


def get_mediawiki_tables():
    """
    Get reflected mediawiki table objects, reflecting only once.

    Returns:
        Tuple of (wbt_item_terms, wbt_property_terms, wbt_term_in_lang,
                  wbt_text_in_lang, wbt_text)
    """
    global _mediawiki_metadata
    if _mediawiki_metadata is None:
        engine = get_engine(mediawiki=True)
        _mediawiki_metadata = sa.MetaData()
        _mediawiki_metadata.reflect(bind=engine, only=[
            "wbt_item_terms",
            "wbt_property_terms",
            "wbt_term_in_lang",
            "wbt_text_in_lang",
            "wbt_text",
        ])
    return _mediawiki_metadata.tables
