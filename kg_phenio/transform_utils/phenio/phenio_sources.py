"""Koza transform for adding knowledge sources to PHENIO."""

from biolink.model import Association  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "phenio_sources"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

have_code = False

# This transform is for enriching PHENIO-derived edges
# with Biolink-compliant knowledge sources.

# This maps CURIE prefixes to infores: names.
infores_sources = {}

primary_knowledge_source = ""
aggregator_knowledge_source = "infores:phenio"

# Association
association = Association(
    id=row["id"],
    subject=row["subject"],
    predicate=row["predicate"],
    object=row["object"],
    category=row["category"],
    relation=row["relation"],
    primary_knowledge_source=primary_knowledge_source,
    aggregator_knowledge_source=aggregator_knowledge_source
)

koza_app.write(association)
