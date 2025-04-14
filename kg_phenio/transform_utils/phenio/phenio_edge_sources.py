"""Koza transform for adding knowledge sources to PHENIO."""

import importlib

from koza.cli_utils import get_koza_app  # type: ignore

from kg_phenio.transform_utils.sources import BAD_PREFIXES, EDGE_SOURCES

source_name = "phenio_edge_sources"

koza_app = get_koza_app(source_name)

# This transform is for enriching PHENIO-derived edges
# with Biolink-compliant knowledge sources.

# This maps CURIE prefixes to infores: names.
# For edges, the source isn't necessarily
# the same as the node source.
# TODO: technically the names should be part of
#       biolink:InformationResource objects
infores_sources = EDGE_SOURCES

common_prefixes = ["BFO", "owl", "RO"]

primary_knowledge_source = "infores:unknown"
aggregator_knowledge_source = ["infores:phenio"]

while (row := koza_app.get_row()) is not None:

    # Ignore redundant category assignments
    if row["predicate"] in ["biolink:category", "biolink:inverseOf"]:
        continue

    subj_curie_prefix = (str(row["subject"]).split(":"))[0]
    if subj_curie_prefix == "OBO":  # See if there's another prefix
        if (str(row["subject"])).startswith("OBO:uberon"):
            subj_curie_prefix = "UBERON"
        else:
            subj_curie_prefix = (str(row["subject"]).split("_"))[0][4:]
    obj_curie_prefix = (str(row["object"]).split(":"))[0]
    relation_prefix = (str(row["relation"]).split(":"))[0]

    if subj_curie_prefix not in BAD_PREFIXES:
        if relation_prefix == "UPHENO":
            infores = "upheno"
        elif obj_curie_prefix == "UPHENO":
            infores = "upheno"
        else:
            infores = infores_sources[subj_curie_prefix]

        object_curie = str(row["object"])

        if str(row["object"]).startswith("http://identifiers.org/hgnc/"):  # Fix URLs
            object_curie = "HGNC:" + str(row["object"]).split("/")[-1]

        primary_knowledge_source = f"infores:{infores}"
    else:
        continue

    # Association

    # The relation or predicate tells us which class to use.
    # We default to generic Association.
    remap_rels_to_aclass = {
        "biolink:has_phenotype": "DiseaseToPhenotypicFeatureAssociation",
        "biolink:disease_has_location": "DiseaseOrPhenotypicFeatureToLocationAssociation",
    }

    # These relations have Biolink maps
    remap_rels_to_preds = {
        "BFO:0000050": "biolink:part_of",
        "BFO:0000051": "biolink:has_part",
        "BFO:0000062": "biolink:preceded_by",
        "BFO:0000063": "biolink:precedes",
        "BFO:0000066": "biolink:occurs_in",
        "RO:0000056": "biolink:participates_in",
        "RO:0000057": "biolink:has_participant",
        "RO:0000086": "biolink:has_attribute",
        "RO:0000087": "biolink:has_attribute",
        "RO:0004020": "biolink:has_participant",
        "RO:0004021": "biolink:has_participant",
        "RO:0004024": "biolink:disrupts",
        "RO:0004026": "biolink:disease_has_location",
        "RO:0004028": "biolink:caused_by",
        "RO:0009501": "biolink:caused_by",
        "OBO:mondo#disease_triggers": "biolink:causes",
    }

    # Some namespace combinations require special handling
    if subj_curie_prefix == "MONDO" and obj_curie_prefix == "HP":
        relation = str(row["relation"])
        predicate = "biolink:has_phenotype"
    elif subj_curie_prefix == "MONDO" and obj_curie_prefix == "GO":
        relation = str(row["relation"])
        if relation in remap_rels_to_preds:
            predicate = remap_rels_to_preds[relation]
        else:
            predicate = str(row["predicate"])
    elif subj_curie_prefix == "MONDO" and obj_curie_prefix == "UBERON":
        relation = str(row["relation"])
        predicate = "biolink:disease_has_location"
    else:
        relation = str(row["relation"])
        predicate = str(row["predicate"])

    # Assign the correct Biolink association class
    if relation in remap_rels_to_aclass:
        category_name = remap_rels_to_aclass[relation]
    elif predicate in remap_rels_to_aclass:
        category_name = remap_rels_to_aclass[predicate]
    else:
        category_name = "Association"
    AssocClass = getattr(
        importlib.import_module("biolink_model.datamodel.pydanticmodel_v2"),
        category_name,
    )

    # These are default values for these slots
    agent_type = "not_provided"
    knowledge_level = "not_provided"

    association = AssocClass(
        id=row["id"],
        subject=row["subject"],
        predicate=predicate,
        original_predicate=relation,
        object=object_curie,
        primary_knowledge_source=primary_knowledge_source,
        aggregator_knowledge_source=aggregator_knowledge_source,
        agent_type=agent_type,
        knowledge_level=knowledge_level,
    )

    koza_app.write(association)
