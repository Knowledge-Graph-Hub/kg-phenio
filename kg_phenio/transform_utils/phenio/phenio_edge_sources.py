"""Koza transform for adding knowledge sources to PHENIO."""
import importlib

from biolink.model import Association  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "phenio_edge_sources"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

valid = True

# This transform is for enriching PHENIO-derived edges
# with Biolink-compliant knowledge sources.

# This maps CURIE prefixes to infores: names.
# For edges, the source isn't necessarily
# the same as the node source.
# TODO: technically the names should be part of
#       biolink:InformationResource objects
infores_sources = {
    "APO": "apo",  # Ascomycete phenotype ontology - cat only
    "BFO": "bfo",
    "BSPO": "upheno",  # Biological Spatial Ontology - from Upheno
    "BTO": "bto",  # BRENDA vocab - cat only
    "CHEBI": "chebi",
    "CHR": "mondo",  # Chromosome ID - from MONDO
    "CIO": "cio",  # Confidence Information - cat only
    "CL": "cl",
    "CLO": "clo",  # Cell Line - cat only
    "DDANAT": "ddanat",  # Dictyostelium discoideum anatomy - cat only
    "DOID": "doid",  # Disease ID - cat only
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
    "MFOMD": "mondo",  # Mental Disease - ref'd by MONDO
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
    "OBO": "unknown",  # a messy one - usually not OBO, though
    "OGMS": "ogms",
    "OIO": "oio",
    "OMIM": "omim",  # OMIM - cat only
    "Orphanet": "orphanet",
    "PATO": "pato",
    "PCO": "pco",
    "PO": "po",
    "PR": "pr",
    "PW": "pw",
    "RO": "ro",
    "RXCUI": "rxnorm",  # RXNORM - cat only
    "SEPIO": "sepio",
    "SO": "so",
    "SIO": "sio",
    "STATO": "stato",
    "TO": "to",  # Plant Trait - cat only
    "UBERON": "uberon",
    "UMLS": "umls",  # UMLS - cat only
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
    "pav": "pav",  # PAV onto - cat only
    "rdf": "rdf",
    "rdfs": "rdfs",
    "skos": "skos",
}

bad_prefixes = ["http", "https", "DATA", "WD_Entity", "WD_Prop"]

common_prefixes = ["BFO", "owl", "RO"]

primary_knowledge_source = "infores:unknown"
aggregator_knowledge_source = "infores:phenio"

subj_curie_prefix = (str(row["subject"]).split(":"))[0]
obj_curie_prefix = (str(row["object"]).split(":"))[0]
relation_prefix = (str(row["relation"]).split(":"))[0]

# This makes an assumption that the subject determines
# the source, which isn't always the case,
if subj_curie_prefix not in bad_prefixes:
    if relation_prefix == "UPHENO":
        infores = "upheno"
    else:
        infores = infores_sources[subj_curie_prefix]
    primary_knowledge_source = f"infores:{infores}"

# Association

# The relation tells us which class to use.
# We default to generic Association.
# TODO: add more to this map
remap_rels = {
    "UPHENO:0000003": "DiseaseOrPhenotypicFeatureToLocationAssociation"
}
relation = str(row["relation"])
if relation in remap_rels:
    category_name = remap_rels[relation]
else:
    category_name = "Association"
AssocClass = getattr(importlib.import_module("biolink.model"), category_name)

if valid:
    association = AssocClass(
        id=row["id"],
        subject=row["subject"],
        predicate=row["predicate"],
        object=row["object"],
        original_predicate=row["relation"],
        primary_knowledge_source=primary_knowledge_source,
        aggregator_knowledge_source=aggregator_knowledge_source,
    )

    koza_app.write(association)
