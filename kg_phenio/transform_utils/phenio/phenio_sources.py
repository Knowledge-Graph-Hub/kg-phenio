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
# TODO: technically the names should be part of
#       biolink:InformationResource objects
infores_sources = {
    "BFO": "bfo",
    "biolink": "biolink",
    "CHEBI": "chebi",
    "CARO": "caro",
    "CL": "cl",
    "ECO": "eco",
    "OBO": "obo", # Not quite right - these are extra OBO prefixes
    "EMAPA": "emapa",
    "ENVO": "envo",
    "FAO": "fao",
    "FBbt": "fbbt",
    "FMA": "fma",
    "faldo": "faldo",
    "foaf": "foaf",
    "FlyBase": "flybase",
    "FOODON": "foodon",
    "GO": "go",
    "HP": "hp",
    "IAO": "iao",
    "MA": "ma",
    "MF": "mf",
    "MONDO": "mondo",
    "MPATH": "mpath",
    "MP": "mp",
    "NBO": "nbo",
    "NCBITaxon": "ncbitaxon",
    "NCIT": "ncit",
    "OBA": "oba",
    "OBI": "obi",
    "OGMS": "ogms",
    "OIO": "oio",
    "owl": "owl",
    "PATO": "pato",
    "PCO": "pco",
    "PO": "po",
    "PR": "pr",
    "RO": "ro",
    "RXCUI": "rxnorm", # TODO: check on these edges
    "SO": "so",
    "STATO": "stato",
    "UBERON": "uberon",
    "UMLS": "umls", # TODO: check on these edges
    "UPHENO": "upheno",
    "WBPhenotype": "wbphenotype",
    "WBbt": "wbbt",
    "ZFA": "zfa",
    "ZP": "zp",
}

bad_prefixes = ["http", "DATA"]

common_prefixes = ["BFO", "owl", "RO"]

primary_knowledge_source = "infores:unknown"
aggregator_knowledge_source = "infores:phenio"

subj_curie_prefix = (str(row["subject"]).split(":"))[0]
obj_curie_prefix = (str(row["object"]).split(":"))[0]

# TODO: make this more specific, as it won't always be true
if subj_curie_prefix not in bad_prefixes:
    infores = infores_sources[subj_curie_prefix]
    primary_knowledge_source = f"infores:{infores}"
    
if row["category"] in ["biolink:category"]:
    valid = False

# TODO: assign more specific association type
# TODO: include relation type
#       Biolink/Koza don't like assigning it directly
#       as it isn't an association slot

# Association
if valid:
    association = Association(
        id=row["id"],
        subject=row["subject"],
        predicate=row["predicate"],
        object=row["object"],
        # relation=row["relation"],
        primary_knowledge_source=primary_knowledge_source,
        aggregator_knowledge_source=aggregator_knowledge_source,
    )

    koza_app.write(association)
