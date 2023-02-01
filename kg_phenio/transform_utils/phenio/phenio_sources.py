"""Koza transform for adding knowledge sources to PHENIO."""

from biolink.model import Association  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "phenio_sources"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

valid = True

# This transform is for enriching PHENIO-derived edges
# with Biolink-compliant knowledge sources.

# This maps CURIE prefixes to infores: names.
infores_sources = {}

primary_knowledge_source = "infores:unknown"
aggregator_knowledge_source = "infores:phenio"

subj_curie_prefix = (str(row["subject"]).split(":"))[0]

if subj_curie_prefix in infores_sources:
    infores = infores_sources[subj_curie_prefix]
    primary_knowledge_source = f"infores:{infores}"

if row["category"] in ["biolink:category"]:
    valid = False

# TODO: assign more specific association type
# TODO: include relation type
#       Biolink/Koza don't like assigning it directly
#       as it isn't an association slot

# Association
association = Association(
    id=row["id"],
    subject=row["subject"],
    predicate=row["predicate"],
    object=row["object"],
    #relation=row["relation"],
    primary_knowledge_source=primary_knowledge_source,
    aggregator_knowledge_source=aggregator_knowledge_source
)

if valid:
    koza_app.write(association)
