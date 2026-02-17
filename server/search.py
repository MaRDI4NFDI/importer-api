import sqlalchemy as db
from sqlalchemy import and_
import urllib.parse
from .connection import get_engine, get_mediawiki_tables


def search_items(label):
    label = urllib.parse.unquote(label)
    label = bytes(label, "utf-8")
    is_truncated = False
    if len(label) > 250:
        label = label[:250]
        is_truncated = True

    engine = get_engine(mediawiki=True)
    tables = get_mediawiki_tables()
    wbt_item_terms = tables["wbt_item_terms"]
    wbt_term_in_lang = tables["wbt_term_in_lang"]
    wbt_text_in_lang = tables["wbt_text_in_lang"]
    wbt_text = tables["wbt_text"]

    if is_truncated:
        text_condition = wbt_text.columns.wbx_text.like(label + b"%")
    else:
        text_condition = (wbt_text.columns.wbx_text == label)

    def query_wikidata_table(field_type):
        # field_type = 1 : Label
        # field_type = 2 : Alias
        # see: https://doc.wikimedia.org/Wikibase/REL1_41/php/docs_sql_wbt_type.html
        with engine.connect() as connection:
            try:
                query = (
                    db.select(wbt_item_terms.columns.wbit_item_id)
                    .join(
                        wbt_term_in_lang,
                        wbt_item_terms.columns.wbit_term_in_lang_id
                        == wbt_term_in_lang.columns.wbtl_id,
                    )
                    .join(
                        wbt_text_in_lang,
                        wbt_term_in_lang.columns.wbtl_text_in_lang_id
                        == wbt_text_in_lang.columns.wbxl_id,
                    )
                    .join(
                        wbt_text,
                        wbt_text.columns.wbx_id
                        == wbt_text_in_lang.columns.wbxl_text_id,
                    )
                    .where(
                        and_(
                            text_condition,
                            wbt_term_in_lang.columns.wbtl_type_id == field_type,
                            wbt_text_in_lang.columns.wbxl_language
                            == bytes("en", "utf-8"),
                        )
                    )
                )
                results = connection.execute(query).fetchall()
                return [f"Q{str(result[0])}" for result in results]
            except Exception as e:
                raise Exception(
                    "Error attempting to read mappings from database\n{}".format(e)
                )

    entity_id = query_wikidata_table(field_type=1)
    entity_id += query_wikidata_table(field_type=2)
    return {"QID": entity_id}


def search_properties(label):
    label = urllib.parse.unquote(label)
    engine = get_engine(mediawiki=True)
    tables = get_mediawiki_tables()
    wbt_property_terms = tables["wbt_property_terms"]
    wbt_term_in_lang = tables["wbt_term_in_lang"]
    wbt_text_in_lang = tables["wbt_text_in_lang"]
    wbt_text = tables["wbt_text"]

    with engine.connect() as connection:
        try:
            query = (
                db.select(wbt_property_terms.columns.wbpt_property_id)
                .join(
                    wbt_term_in_lang,
                    wbt_term_in_lang.columns.wbtl_id
                    == wbt_property_terms.columns.wbpt_term_in_lang_id,
                )
                .join(
                    wbt_text_in_lang,
                    wbt_term_in_lang.columns.wbtl_text_in_lang_id
                    == wbt_text_in_lang.columns.wbxl_id,
                )
                .join(
                    wbt_text,
                    wbt_text.columns.wbx_id == wbt_text_in_lang.columns.wbxl_text_id,
                )
                .where(
                    db.and_(
                        wbt_text.columns.wbx_text == bytes(label, "utf-8"),
                        wbt_term_in_lang.columns.wbtl_type_id == 1,
                        wbt_text_in_lang.columns.wbxl_language == bytes("en", "utf-8"),
                    )
                )
            )
            results = connection.execute(query).fetchall()
            result = ""
            if results:
                result = f"P{str(results[0][0])}"

        except Exception as e:
            raise Exception(
                "Error attempting to read mappings from database\n{}".format(e)
            )

        return {"PID": result}
