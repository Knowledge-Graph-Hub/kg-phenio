import logging
import re

from SPARQLWrapper import SPARQLWrapper, JSON # type: ignore
import rdflib
from rdflib import Graph
from rdflib.plugins.sparql.processor import SPARQLResult

def run_remote_query(query: str, endpoint: str, return_format=JSON) -> dict:
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(return_format)
    results = sparql.query().convert()

    return results # type: ignore

def run_local_query(query: str, local_endpoint: str) -> tuple:
    g = Graph()
    g.parse(local_endpoint)
    print(f"Parsed {len(g)} triples from {local_endpoint}.")
    results = g.query(query)
    print(f"Query yielded {len(results)} results.")
    return (g, results) # type: ignore

def add_result_to_graph(graph: Graph, addition: SPARQLResult) -> Graph:
    """
    Given an RDF Graph and a query result, combines them and returns the
    new graph.
    """
    print(f"Before update: {len(graph)} triples found.")
    for result in addition:
        # This may need to be more specific, either in the method call
        # or as an INSERT query
        graph.add(result)  
    print(f"After update: {len(graph)} triples found.")
    return graph

def update_graph(graph: Graph, addition: Graph) -> Graph:
    """
    Given two RDF Graphs, combines them and returns the
    new graph.
    """
    g = Graph()
    g.parse(graph)
    print(f"Before update: {len(g)} triples found.")
    g.parse(addition)
    print(f"After update: {len(g)} triples found.")
    return g # type: ignore

def parse_query_rq(rq_file) -> dict:
    """

    Args:
        rq_file: sparql query in grlc rq format

    Returns: dict with parsed info about sparql query

    """
    parsed_rq = dict()
    with open(rq_file) as r:
        query = ''
        for line in r:
            if line.isspace():
                continue
            elif re.match('^\=\+ ', line):
                (key, value) = re.sub('^\=\+ ', '', line).rstrip().split(' ', maxsplit=1)
                parsed_rq[key] = value
            else:
                query += line
        parsed_rq['query'] = query
    return parsed_rq


def result_dict_to_tsv(result_dict: dict, outfile: str) -> None:
    with open(outfile, 'wt') as f:
        # header
        f.write("\t".join(result_dict['head']['vars']) + "\n")
        for row in result_dict['results']['bindings']:
            row_items = []
            for col in result_dict['head']['vars']:
                try:
                    row_items.append(row[col]['value'])
                except KeyError:
                    logging.error('Problem retrieving result for col %s in row %s' %
                                  (col, "\t".join(row)))
                    row_items.append('ERROR')
            try:
                f.write("\t".join(row_items) + "\n")
            except:
                pass