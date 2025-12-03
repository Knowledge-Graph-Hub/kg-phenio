"""Koza ingest for Upheno phenotype maps."""

import uuid

from biolink_model.datamodel.pydanticmodel_v2 import (Association,
                                                      PhenotypicFeature)
from koza.cli_utils import get_koza_app

source_name = "upheno_mapping_all"
koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Include all major model organism phenotype ontologies
desired_types = [
    "HP",           # Human Phenotype Ontology
    "MP",           # Mammalian/Mouse Phenotype Ontology
    "ZP",           # Zebrafish Phenotype Ontology
    "XPO",          # Xenopus Phenotype Ontology
    "WBPhenotype",  # C. elegans/Worm Phenotype
    "FBcv",         # Drosophila/Fly Phenotype
    "DDPHENO",      # Dictyostelium Phenotype
    "PHIPO",        # Planarian Phenotype
    "FYPO",         # Fission Yeast Phenotype
    "PLANP",        # Plant Phenotype
]

# Only process exact match predicates
if row["predicate_id"] != "semapv:crossSpeciesExactMatch":
    pass  # Skip non-exact matches
else:
    # Entities - IDs are already in CURIE format, no parsing needed
    p1 = PhenotypicFeature(
        id=row["subject_id"],
        name=row["subject_label"],
        category=["biolink:PhenotypicFeature"],
    )
    p2 = PhenotypicFeature(
        id=row["object_id"],
        name=row["object_label"],
        category=["biolink:PhenotypicFeature"],
    )

    # Association

    # These are default values for these slots
    agent_type = "not_provided"
    knowledge_level = "not_provided"

    primary_knowledge_source = "infores:upheno"
    aggregator_knowledge_source = ["infores:phenio"]

    if p1.id[0:2] in desired_types and p2.id[0:2] in desired_types:
        association = Association(
            id="uuid:" + str(uuid.uuid1()),
            subject=p1.id,
            predicate="biolink:same_as",
            object=p2.id,
            original_predicate="semapv:crossSpeciesExactMatch",
            primary_knowledge_source=primary_knowledge_source,
            aggregator_knowledge_source=aggregator_knowledge_source,
            agent_type=agent_type,
            knowledge_level=knowledge_level,
        )

        koza_app.write(p1, association, p2)
