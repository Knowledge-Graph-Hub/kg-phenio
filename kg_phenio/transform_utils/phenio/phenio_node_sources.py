"""Koza transform for adding knowledge sources to PHENIO."""

import importlib
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "phenio_node_sources"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

valid = True

# This transform is for enriching PHENIO-derived nodes
# with Biolink-compliant knowledge sources,
# in the provided_by slot.

# This maps CURIE prefixes to infores: names.

infores_sources = {
    "APO": "apo",  # TODO: check this one
    "BFO": "bfo",
    "BSPO": "bspo",  # TODO: check this one
    "BTO": "bto",  # TODO: check this one
    "CARO": "caro",
    "CHEBI": "chebi",
    "CHR": "chr",  # TODO: check this one
    "CIO": "cio",  # TODO: check this one
    "CL": "cl",
    "CLO": "clo",  # TODO: check this one
    "DDANAT": "ddanat",  # TODO: check this one
    "DOID": "doid",  # TODO: check this one
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
    "MFOMD": "mfomd",  # TODO: check this
    "MI": "mi",
    "MONDO": "mondo",
    "MP": "mp",
    "MPATH": "mpath",
    "NBO": "nbo",
    "NCBITaxon": "ncbitaxon",
    "NCIT": "ncit",
    "OBA": "oba",
    "OBAN": "oban",
    "OBI": "obi",
    "OBO": "obo",  # TODO: Not quite right - these are extra OBO prefixes
    "OGMS": "ogms",
    "OIO": "oio",
    "OMIM": "omim",  # TODO: certainly check these
    "Orphanet": "orphanet",
    "PATO": "pato",
    "PCO": "pco",
    "PO": "po",
    "PR": "pr",
    "PW": "pw",
    "RO": "ro",
    "RXCUI": "rxnorm",  # TODO: check on these edges
    "SEPIO": "sepio",
    "SO": "so",
    "SIO": "sio",
    "STATO": "stato",
    "TO": "to",  # TODO: check on these
    "UBERON": "uberon",
    "UMLS": "umls",  # TODO: check on these edges
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
    "pav": "pav",  # TODO: check on this one
    "rdf": "rdf",
    "rdfs": "rdfs",
    "skos": "skos",
}

bad_prefixes = ["http", "https", "DATA", "WD_Entity", "WD_Prop"]

primary_knowledge_source = "infores:unknown"

node_curie_prefix = (str(row["id"]).split(":"))[0]

# The category tells us which class to use.
category_name = (str(row["category"]).split(":"))[1]
NodeClass = getattr(importlib.import_module("biolink.model"), category_name)

# TODO: make this more specific, as it won't always be true
if node_curie_prefix not in bad_prefixes:
    infores = infores_sources[node_curie_prefix]
    primary_knowledge_source = f"infores:{infores}"

# Association
if valid:
    node = NodeClass(
        id=row["id"],
        category=row["category"],
        name=row["name"],
        description=row["description"],
        provided_by=primary_knowledge_source,
    )

    koza_app.write(node)
