"""Koza ingest for Upheno phenotype maps."""

import uuid

from biolink_model.datamodel.pydanticmodel_v2 import (Association,
                                                      PhenotypicFeature)
from koza.cli_utils import get_koza_app

source_name = "upheno_mapping_all"
koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# We just want mouse (MP) and human (HP) phenotypes.
desired_types = ["MP", "HP"]

# Entities

p1 = PhenotypicFeature(
    id=(((row["p1"]).split("/"))[-1]).replace("_", ":"),
    iri=row["p1"],
    name=row["label_x"],
    category=["biolink:PhenotypicFeature"],
)
p2 = PhenotypicFeature(
    id=(((row["p2"]).split("/"))[-1]).replace("_", ":"),
    iri=row["p2"],
    name=row["label_y"],
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
        original_predicate="skos:exactMatch",
        primary_knowledge_source=primary_knowledge_source,
        aggregator_knowledge_source=aggregator_knowledge_source,
        agent_type=agent_type,
        knowledge_level=knowledge_level,
    )

    koza_app.write(p1, association, p2)
