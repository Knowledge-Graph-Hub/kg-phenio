"""Koza transform for adding knowledge sources to PHENIO."""

import importlib

from koza.cli_utils import get_koza_app  # type: ignore

from kg_phenio.transform_utils.sources import EDGE_INFORES_SOURCES

source_name = "phenio_edge_sources"

koza_app = get_koza_app(source_name)

# This transform is for enriching PHENIO-derived edges
# with Biolink-compliant knowledge sources.

# This maps CURIE prefixes to infores: names.
# For edges, the source isn't necessarily
# the same as the node source.
# TODO: technically the names should be part of
#       biolink:InformationResource objects
infores_sources = EDGE_INFORES_SOURCES

bad_prefixes = [
    "DATA",
    "PHENIO",
    "WD_Entity",
    "WD_Prop",
    "chebi#is",
    "core#connected",
    "core#distally",
    "core#innervated",
    "core#subdivision",
    "doid#derives",
    "doid#has",
    "emapa#Tmp",
    "emapa#group",
    "emapa#group_term",
    "http",
    "https",
    "mondo#disease",
    "ncit#C142749",
    "nbo#by",
    "nbo#has",
    "nbo#in",
    "nbo#is",
    "stato.owl#is",
    "stato.owl#response",
]

common_prefixes = ["BFO", "owl", "RO"]

primary_knowledge_source = "infores:unknown"
aggregator_knowledge_source = ["infores:phenio"]

while (row := koza_app.get_row()) is not None:
    valid = True

    subj_curie_prefix = (str(row["subject"]).split(":"))[0]
    if subj_curie_prefix == "OBO":  # See if there's another prefix
        if (str(row["subject"])).startswith("OBO:uberon"):
            subj_curie_prefix = "UBERON"
        else:
            subj_curie_prefix = (str(row["subject"]).split("_"))[0][4:]
    obj_curie_prefix = (str(row["object"]).split(":"))[0]
    relation_prefix = (str(row["relation"]).split(":"))[0]

    if subj_curie_prefix not in bad_prefixes:
        if relation_prefix == "UPHENO":
            infores = "upheno"
        elif obj_curie_prefix == "UPHENO":
            infores = "upheno"
        else:
            infores = infores_sources[subj_curie_prefix]
        primary_knowledge_source = f"infores:{infores}"

    # Association

    # The relation or predicate tells us which class to use.
    # We default to generic Association.
    remap_rels = {
        "biolink:has_phenotype": "DiseaseToPhenotypicFeatureAssociation",
        "UPHENO:0000003": "DiseaseOrPhenotypicFeatureToLocationAssociation",
    }

    if subj_curie_prefix == "MONDO" and obj_curie_prefix == "HP":
        relation = str(row["relation"])
        predicate = "biolink:has_phenotype"
    else:
        relation = str(row["relation"])
        predicate = str(row["predicate"])

    if relation in remap_rels:
        category_name = remap_rels[relation]
    elif predicate in remap_rels:
        category_name = remap_rels[predicate]
    else:
        category_name = "Association"
    AssocClass = getattr(
        importlib.import_module("biolink_model.datamodel.pydanticmodel_v2"),
        category_name,
    )

    # These are default values for these slots
    agent_type = "not_provided"
    knowledge_level = "not_provided"

    if valid:
        association = AssocClass(
            id=row["id"],
            subject=row["subject"],
            predicate=predicate,
            relation=relation,
            object=row["object"],
            original_predicate=row["relation"],
            primary_knowledge_source=primary_knowledge_source,
            aggregator_knowledge_source=aggregator_knowledge_source,
            agent_type=agent_type,
            knowledge_level=knowledge_level,
        )

        koza_app.write(association)
