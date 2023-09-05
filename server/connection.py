import os
import sqlalchemy as db

def create_engine():
    """
    Creates SQLalchemy engine

    Returns:
        SQLalchemy engine
    """
    db_user = os.environ["MYSQL_USER"]
    db_pass = os.environ["MYSQL_PASSWORD"]
    db_name = os.environ["MYSQL_DATABASE"]
    db_host = os.environ["DB_HOST"]
    return db.create_engine(
        f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}"
    )