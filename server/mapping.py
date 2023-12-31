import re
import sqlalchemy as db

from .connection import create_engine

def get_mapping(entity_id):
    match_wikidata = re.match(r'wdt?:([PQ]\d+)', entity_id)
    match_local = re.match(r'[PQ]\d+', entity_id)
    if match_wikidata:
        wikidata_id = match_wikidata.group(1)
        local_id = get_local_id(wikidata_id)
        if local_id:
            return {'local_id': local_id,
                    'wikidata_id': wikidata_id}
    if match_local:
        local_id = match_local.group(0)
        wikidata_id = get_wikidata_id(local_id)
        if wikidata_id:
            return {'local_id': local_id,
                    'wikidata_id': wikidata_id}      

def get_local_id(wikidata_id):
    engine = create_engine()
    metadata = db.MetaData()
    table = db.Table(
        "wb_id_mapping", 
        metadata, 
        autoload_with=engine
    )
    sql = db.select(table.columns['local_id']).where(
        table.columns.wikidata_id == wikidata_id,
    )
    with engine.connect() as connection:
        db_result = connection.execute(sql).fetchone()
    if db_result:
        return db_result[0]

def get_wikidata_id(local_id):
    engine = create_engine()
    metadata = db.MetaData()
    table = db.Table(
        "wb_id_mapping", 
        metadata, 
        autoload_with=engine
    )
    sql = db.select(table.columns['wikidata_id']).where(
        table.columns.local_id == local_id,
    )
    with engine.connect() as connection:
        db_result = connection.execute(sql).fetchone()
    if db_result:
        return db_result[0]