"""Maps from other namespaces to BioLink Model, for PHENIO transorm."""

# Should this be SSSOM? Probably.

# BioLink relations with corresponding Association classes
REMAP_RELS_TO_ACLASS = {
    "biolink:has_phenotype": "DiseaseToPhenotypicFeatureAssociation",
    "biolink:disease_has_location": "DiseaseOrPhenotypicFeatureToLocationAssociation",
}

# Other namespaces with BioLink relations
REMAP_RELS_TO_PREDS = {
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
