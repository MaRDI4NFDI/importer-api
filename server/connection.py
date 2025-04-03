import os
import sqlalchemy as db

def create_engine(mediawiki=False):
    """
    Creates SQLalchemy engine

    Returns:
        SQLalchemy engine
    """
    db_user = os.environ["MYSQL_USER"]
    db_pass = os.environ["MYSQL_PASSWORD"]
    db_name = os.environ["MYSQL_DATABASE"]
    if mediawiki:
        db_name = 'my_wiki'
    db_host = os.environ["DB_HOST"]
    return db.create_engine(
        url="mariadb+mariadbconnector://{0}:{1}@{2}/{3}".format(
            db_user, db_pass, db_host, db_name
        )
    )  