"""Source assignments for transforms."""

EDGE_INFORES_SOURCES = {
    "APO": "apo",  # Ascomycete phenotype ontology - cat only
    "BFO": "bfo",
    "BSPO": "upheno",  # Biological Spatial Ontology - from Upheno
    "BTO": "bto",  # BRENDA vocab - cat only
    "CARO": "caro",  # CARO - cat only
    "CHEBI": "chebi",
    "CHR": "mondo",  # Chromosome ID - from MONDO
    "CIO": "cio",  # Confidence Information - cat only
    "CL": "cl",
    "CLO": "clo",  # Cell Line - cat only
    "COB": "cob",
    "DDANAT": "ddanat",  # Dictyostelium discoideum anatomy - cat only
    "DDPHENO": "ddpheno",
    "DOID": "doid",  # Disease ID - cat only
    "ECO": "eco",
    "ECTO": "ecto",
    "ExO": "exo",
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
    "GOREL": "go",
    "HP": "hp",
    "HsapDv": "HsapDv",
    "IAO": "iao",
    "INO": "ino",
    "MA": "ma",
    "MAXO": "maxo",
    "MF": "mf",
    "MFOMD": "mondo",  # Mental Disease - ref'd by MONDO
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
    "OBO": "unknown",  # a messy one - may not be OBO though
    "OGMS": "ogms",
    "OIO": "oio",
    "OMIM": "omim",  # OMIM - cat only
    "OMIT": "omit",
    "Orphanet": "orphanet",
    "PATO": "pato",
    "PCO": "pco",
    "PO": "po",
    "PR": "pr",
    "PW": "pw",
    "RO": "ro",
    "RnorDv": "rnordv",
    "RXCUI": "rxnorm",  # RXNORM - cat only
    "SEPIO": "sepio",
    "SO": "so",
    "SIO": "sio",
    "SNOMED": "snomed",
    "STATO": "stato",
    "TO": "to",  # Plant Trait - cat only
    "TS": "ts",  # almost always with EMAPA
    "UBERON": "uberon",
    "UMLS": "umls",  # UMLS - cat only
    "UPHENO": "upheno",
    "WBPhenotype": "wbphenotype",
    "WBBT": "wbbt",
    "WBbt": "wbbt",
    "WBls": "wbls",
    "XAO": "xao",
    "XCO": "xco",
    "XPO": "xpo",
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

NODE_INFORES_SOURCES = {
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
    "DDPHENO": "ddpheno",
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