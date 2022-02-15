#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 21:24:37 2020

@author: Nicolas Matentzoglu, EMBL-EBI
"""

import os, shutil, sys
import ruamel.yaml
import warnings
import urllib.request
import requests
import pandas as pd
import re
from subprocess import check_call,CalledProcessError
from lib import *

### Configuration
warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)

config_file = sys.argv[1]
print(config_file)
config = okpk_config(config_file)

TIMEOUT=str(config.get_external_timeout())
ws = config.get_working_directory()
robot_opts=config.get_robot_opts()

#print("REMOVE ENV ENV")
#print("REMOVE ENV ENV")
#print("REMOVE ENV ENV")
#print("REMOVE ENV ENV")
#os.environ['BUILDDIR']='build'
#os.environ['SPARQLDIR']='sparql'

ontology_dir = os.path.join("ontologies")
build_dir = os.path.join(os.environ['BUILDDIR'])
sparql_dir = os.path.join(os.environ['SPARQLDIR'])


cdir(ontology_dir)
cdir(build_dir)

if config.is_clean_dir():
    print("Cleanup..")
    shutil.rmtree(ontology_dir)
    os.makedirs(ontology_dir)
    shutil.rmtree(build_dir)
    os.makedirs(build_dir)

common_properties = config.get_global_properties()
kgx_nodes_sparql = os.path.join(sparql_dir,"kgx_nodes.sparql")
kgx_edges_sparql = os.path.join(sparql_dir,"kgx_edges.sparql")
kgx_edges_cl_sparql = os.path.join(sparql_dir,"kgx_edges_cl.sparql")
kgx_annotations_sparql = os.path.join(sparql_dir,"kgx_annotations.sparql")
construct_kgx_types_sparql = os.path.join(sparql_dir,"construct_kgx_types.sparql")

skip = True

print("Preprocessing ontologies for easy ingestion into knowledge graphs")

for o in config.get_ontologies():
    print("Preparing configuration {}...".format(o))
    o_build_dir = os.path.join(build_dir,o)
    o_ontology_dir = os.path.join(ontology_dir,o)
    o_role_chains = os.path.join(o_build_dir,"role_chains_{}.owl".format(o))
    o_seed_table = os.path.join(o_build_dir,"seed_{}.csv".format(o))
    o_seed = os.path.join(o_build_dir,"seed_{}.txt".format(o))
    o_seed_sparql = os.path.join(o_build_dir,"seed_{}.sparql".format(o))
    o_biolink_sparql = os.path.join(o_build_dir,"biolink_{}.sparql".format(o))
    o_biolink_category_ttl  = os.path.join(o_build_dir,"biolink_categories_{}.ttl".format(o))
    o_biolink_relations_ttl  = os.path.join(o_build_dir,"biolink_relations_{}.ttl".format(o))
    o_biolink_update_sparql = os.path.join(o_build_dir,"biolink_update_{}.sparql".format(o))
    o_count_object_properties_sparql = os.path.join(o_build_dir,"count_object_properties_{}.sparql".format(o))
    o_count_annotation_properties_sparql = os.path.join(o_build_dir,"count_annotation_properties_{}.sparql".format(o))
    o_count_object_properties_csv = os.path.join(o_ontology_dir,"count_object_properties_{}.csv".format(o))
    o_count_annotation_properties_csv = os.path.join(o_ontology_dir,"count_annotation_properties_{}.csv".format(o))
    o_enriched = os.path.join(o_build_dir,"{}_enriched.owl".format(o))
    o_reduced = os.path.join(o_build_dir,"{}_reduced.owl".format(o))
    o_finished = os.path.join(o_ontology_dir,"{}_finished.owl".format(o))
    o_biolink = os.path.join(o_build_dir,"{}_biolink.owl".format(o))
    o_kg_json = os.path.join(o_ontology_dir,"{}_kg.json".format(o))
    o_kg_nodes_tsv = os.path.join(o_ontology_dir,"kgx_{}_nodes.csv".format(o))
    o_kg_edges_tsv = os.path.join(o_ontology_dir,"kgx_{}_edges.csv".format(o))
    o_kg_annotations_tsv = os.path.join(o_ontology_dir,"kgx_{}_annotations.csv".format(o))
    
    cdir(o_build_dir)
    cdir(o_ontology_dir)
    
    # Config
    o_roots = config.get_roots(o)
    o_properties = config.get_ontology_properties(o)
    o_annotation_properties = config.get_ontology_annotation_properties(o)
    o_materialise_properties = config.get_ontology_properties(o,True)
    # Prepare SPARQL queries and OWL injections
    prepare_role_chains(o,config.get_role_chains(o),config.get_curie_map(),o_role_chains)
    prepare_sparql_count_object_properties(o,o_roots,config.get_curie_map(),o_count_object_properties_sparql)
    prepare_sparql_count_annotation_properties(o,o_roots,config.get_curie_map(),o_count_annotation_properties_sparql)
    prepare_entities_of_interest(o,o_roots,o_properties,config.get_curie_map(),o_seed_sparql)
    prepare_ttl_biolink_relations(o,config.get_biolink_relation_map(o),config.get_curie_map(),o_biolink_relations_ttl)
    biolink_annotations_sparqls = prepare_sparql_biolink_annotations(o,config.get_biolink_category_map(o),config.get_curie_map(),o_build_dir)
    
    print("Downloading {}...".format(o))
    o_merge_list = download_from_urls(o,config.get_sources(o),o_build_dir,skip)
    o_merge_list.append(o_role_chains)
    
    print("Enriching {} with implied relations...".format(o))
    if not skip or not os.path.exists(o_enriched):
        robot_okpk_enrich(o_merge_list,o_materialise_properties,o_enriched,TIMEOUT)
    if not skip or not os.path.exists(o_count_annotation_properties_csv):
        robot_query(o_enriched,o_count_annotation_properties_csv,o_count_annotation_properties_sparql,TIMEOUT)
    if not skip or not os.path.exists(o_count_object_properties_csv):
        robot_query(o_enriched,o_count_object_properties_csv,o_count_object_properties_sparql,TIMEOUT)
    
    print("Filtering {} for classes and relationships of interest...".format(o))
    if not skip or not os.path.exists(o_reduced):
        robot_okpk_reduce(o_enriched,o_properties,o_reduced,TIMEOUT)
    if not skip or not os.path.exists(o_seed):
        robot_query(o_reduced,o_seed_table,o_seed_sparql,TIMEOUT)
        prepare_seed_file(o_seed_table,o_annotation_properties,o_seed)
    if not skip or not os.path.exists(o_finished): 
        robot_okpk_finish(o_reduced,o_seed,o_finished,TIMEOUT)
    
    print("Export {} to obographs (JSON)...".format(o))
    if not skip or not os.path.exists(o_kg_json): 
        robot_convert(o_finished,"json",o_kg_json)

    print("Export {} to KGX compliant csv...".format(o))
    if not skip or not os.path.exists(o_biolink):
        robot_update(o_enriched,biolink_annotations_sparqls,o_biolink,TIMEOUT)
        robot_query(o_biolink,o_biolink_category_ttl,construct_kgx_types_sparql,format='ttl',TIMEOUT=TIMEOUT)
        robot_merge([o_finished,o_biolink_category_ttl,o_biolink_relations_ttl],o_biolink,TIMEOUT)
    if not skip or not os.path.exists(o_kg_nodes_tsv):
        robot_query(o_biolink,o_kg_nodes_tsv,kgx_nodes_sparql)
    if not skip or not os.path.exists(o_kg_edges_tsv):
        o_kg_edges_rel_tsv = os.path.join(o_build_dir,"kgx_{}_edges_relations.csv".format(o))
        o_kg_edges_cl_tsv = os.path.join(o_build_dir,"kgx_{}_edges_cl.csv".format(o))
        robot_query(o_biolink,o_kg_edges_rel_tsv,kgx_edges_sparql)
        robot_query(o_biolink,o_kg_edges_cl_tsv,kgx_edges_cl_sparql)
        df_kg_nodes = [pd.read_csv(o_kg_edges_rel_tsv),pd.read_csv(o_kg_edges_cl_tsv)]
        pd.concat(df_kg_nodes).to_csv(o_kg_edges_tsv)
    if not skip or not os.path.exists(o_kg_annotations_tsv):
        robot_query(o_biolink,o_kg_annotations_tsv,kgx_annotations_sparql)



