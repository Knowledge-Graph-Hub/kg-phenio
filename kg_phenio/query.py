"""Query functions."""

import re

from SPARQLWrapper import JSON, SPARQLWrapper  # type: ignore


def run_remote_query(query: str, endpoint: str, return_format=JSON) -> dict:
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(return_format)
    results = sparql.query().convert()

    return results  # type: ignore


def parse_query_rq(rq_file) -> dict:
    """

    Args:
        rq_file: sparql query in grlc rq format

    Returns: dict with parsed info about sparql query

    """
    parsed_rq = dict()
    with open(rq_file) as r:
        query = ""
        for line in r:
            if line.isspace():
                continue
            elif re.match("^\=\+ ", line):
                (key, value) = (
                    re.sub("^\=\+ ", "", line).rstrip().split(" ", maxsplit=1)
                )
                parsed_rq[key] = value
            else:
                query += line
        parsed_rq["query"] = query
    return parsed_rq
