"""Koza transform for adding knowledge sources to PHENIO."""

import importlib

from koza.cli_utils import get_koza_app  # type: ignore

from kg_phenio.transform_utils.sources import NODE_INFORES_SOURCES

source_name = "phenio_node_sources"

SYNONYM = "synonym"

koza_app = get_koza_app(source_name)


# This transform is for enriching PHENIO-derived nodes
# with Biolink-compliant knowledge sources,
# in the provided_by slot.

# This maps CURIE prefixes to infores: names.
infores_sources = NODE_INFORES_SOURCES

bad_prefixes = ["dc", "http", "https", "DATA", "WD_Entity", "WD_Prop"]

primary_knowledge_source = "infores:unknown"

while (row := koza_app.get_row()) is not None:
    valid = True

    node_curie_prefix = (str(row["id"]).split(":"))[0]

    # The category tells us which class to use.
    # Some categories won't fit the model and need
    # to be remapped.
    remap_cats = {
        "OntologyClass": "NamedThing",
        "ChemicalSubstance": "ChemicalEntity",
        "SequenceFeature": "SequenceVariant",
    }
    category_name = (str(row["category"]).split(":"))[1]
    if category_name in remap_cats:
        category_name = remap_cats[category_name]
    NodeClass = getattr(
        importlib.import_module("biolink_model.datamodel.pydanticmodel_v2"),
        category_name,
    )

    # TODO: make this more specific, as it won't always be true
    if node_curie_prefix not in bad_prefixes:
        infores = infores_sources[node_curie_prefix]
        primary_knowledge_source = f"infores:{infores}"

    # Association
    if valid:
        node = NodeClass(
            id=row["id"],
            category=["biolink:" + category_name],
            name=row["name"],
            description=row["description"],
            # turning empty strings into False feels wrong, keeping them empty
            deprecated=bool(row["deprecated"]) if row["deprecated"] else None,
            provided_by=[primary_knowledge_source],
        )

        all_slots = list(node.__dict__.keys())
        if row["iri"]:
            node.iri = row["iri"]
        if row[SYNONYM] and SYNONYM in all_slots:
            node.synonym = (row["synonym"]).split("|")

        if row["subsets"]:
            subsets = (row["subsets"]).split("|")

            if "deprecated" in subsets:
                node.deprecated = True

        if row["xref"]:
            xrefs = (row["xref"]).split("|")
            node.xref = xrefs

        koza_app.write(node)
