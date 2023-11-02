"""Koza transform for adding knowledge sources to PHENIO."""

import importlib

from biolink.model import Attribute
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "phenio_node_sources"

SYNONYM = "synonym"

koza_app = get_koza_app(source_name)


# This transform is for enriching PHENIO-derived nodes
# with Biolink-compliant knowledge sources,
# in the provided_by slot.

# This maps CURIE prefixes to infores: names.

infores_sources = {
    "APO": "apo",
    "BFO": "bfo",
    "BSPO": "bspo",
    "BTO": "bto",
    "CARO": "caro",
    "CHEBI": "chebi",
    "CHR": "chr",
    "CIO": "cio",
    "CL": "cl",
    "CLO": "clo",
    "DDANAT": "ddanat",
    "DOID": "doid",
    "ECO": "eco",
    "EMAPA": "emapa",
    "ENVO": "envo",
    "FAO": "fao",
    "FBbt": "fbbt",
    "FBcv": "fbcv",
    "FMA": "fma",
    "FOODON": "foodon",
    "FlyBase": "flybase",
    "FYPO": "fypo",
    "GENO": "geno",
    "GO": "go",
    "HP": "hp",
    "IAO": "iao",
    "MA": "ma",
    "MF": "mf",
    "MFOMD": "mfomd",
    "MI": "mi",
    "MOD": "mod",
    "MONDO": "mondo",
    "MP": "mp",
    "MPATH": "mpath",
    "NBO": "nbo",
    "NCBITaxon": "ncbitaxon",
    "NCIT": "ncit",
    "OBA": "oba",
    "OBAN": "oban",
    "OBI": "obi",
    "OBO": "obo",  # TODO: clean this up
    "OGMS": "ogms",
    "OIO": "oio",
    "OMIM": "omim",
    "OMIT": "omit",
    "Orphanet": "orphanet",
    "PATO": "pato",
    "PCO": "pco",
    "PO": "po",
    "PR": "pr",
    "PW": "pw",
    "RO": "ro",
    "RXCUI": "rxnorm",
    "SEPIO": "sepio",
    "SNOMED": "snomed",
    "SO": "so",
    "SIO": "sio",
    "STATO": "stato",
    "TO": "to",
    "UBERON": "uberon",
    "UMLS": "umls",
    "UPHENO": "upheno",
    "WBPhenotype": "wbphenotype",
    "WBBT": "wbbt",
    "WBbt": "wbbt",
    "XAO": "xao",
    "XCO": "xco",
    "ZFA": "zfa",
    "ZFS": "zfs",
    "ZP": "zp",
    "biolink": "biolink",
    "dcat": "dcat",
    "dcterms": "dcterms",
    "dctypes": "dctypes",
    "faldo": "faldo",
    "foaf": "foaf",
    "owl": "owl",
    "pav": "pav",
    "rdf": "rdf",
    "rdfs": "rdfs",
    "skos": "skos",
}

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
    NodeClass = getattr(importlib.import_module("biolink.model"), category_name)

    # TODO: make this more specific, as it won't always be true
    if node_curie_prefix not in bad_prefixes:
        infores = infores_sources[node_curie_prefix]
        primary_knowledge_source = f"infores:{infores}"

    if "deprecated" in row["subsets"]:
        attribute = Attribute(id="owl:deprecated", name="deprecated")
    else:
        attribute = Attribute(id="")


    # Association
    if valid:
        node = NodeClass(
            id=row["id"],
            iri=row["iri"],
            category=row["category"],
            name=row["name"],
            description=row["description"],
            provided_by=primary_knowledge_source,
            has_attribute=attribute,
        )
        all_slots = list(node.__dict__.keys())
        if row[SYNONYM] and SYNONYM in all_slots:
            node.synonym = (row["synonym"]).split("|")

        koza_app.write(node)
