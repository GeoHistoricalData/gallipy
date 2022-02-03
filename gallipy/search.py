import routes
import json
from helpers import sync_get
from gallipy.parsers import XmlParser


def search(
    query: str,
    version: str = "1.2",
    operation: str = "searchRetrieve",
    start_record: int = 1,
    maximum_records: int = 15,
    collapsing: bool = True,
):
    params = {
        "version": version,
        "operation": operation,
        "query": query,
        "startRecord": start_record,
        "maximumRecords": maximum_records,
        "collapsing": str(collapsing).lower(),
    }
    return sync_get(routes.sru, XmlParser, params)


def categories(query: str):
    params = {"SRU": query}
    return sync_get(routes.categories, json.loads, params)
