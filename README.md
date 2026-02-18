# PHENIO Knowledge Graph

The PHENIO Knowledge Graph provides the ontological backbone of the Monarch Knowledge Graph. It transforms the [PHENIO](https://github.com/monarch-initiative/phenio) (Phenomics Integrated Ontology) application ontology -- a curated integration of ontologies spanning phenotypes, anatomy, disease, and molecular biology -- into Biolink-compliant knowledge graph format with cross-species phenotype mappings from [uPheno](https://github.com/obophenotype/upheno).

## Data Source

PHENIO integrates ontologies needed for cross-species phenotype comparison and analysis. See the [PHENIO composition docs](https://monarch-initiative.github.io/phenio/composition/) for detailed descriptions of each included ontology.

- [PHENIO releases](https://github.com/monarch-initiative/phenio/releases)
- [uPheno cross-species mappings](https://github.com/obophenotype/upheno)

## Biolink Representation

### PhenotypicFeature

Phenotype terms from species-specific and cross-species phenotype ontologies. This is the largest category in the graph, reflecting PHENIO's primary purpose of enabling cross-species phenotype comparison.

- [uPheno](https://github.com/obophenotype/upheno) — Unified Phenotype Ontology (cross-species phenotype classes)
- [HP](https://hpo.jax.org/) — Human Phenotype Ontology
- [MP](http://www.informatics.jax.org/vocab/mp_ontology) — Mammalian Phenotype Ontology
- [ZP](https://github.com/obophenotype/zebrafish-phenotype-ontology) — Zebrafish Phenotype Ontology
- [XPO](https://github.com/obophenotype/xenopus-phenotype-ontology) — Xenopus Phenotype Ontology
- [WBPhenotype](https://github.com/obophenotype/c-elegans-phenotype-ontology) — C. elegans Phenotype Ontology
- [FYPO](https://github.com/pombase/fypo) — Fission Yeast Phenotype Ontology
- [DDPHENO](https://github.com/obophenotype/dicty-phenotype-ontology) — Dictyostelium Phenotype Ontology
- [DPO](https://github.com/FlyBase/drosophila-phenotype-ontology) — Drosophila Phenotype Ontology
- [OBA](https://obofoundry.org/ontology/oba.html) — Ontology of Biological Attributes

### AnatomicalEntity

Anatomical structures from species-specific and cross-species anatomy ontologies, used as building blocks for phenotype definitions and expression data.

- [UBERON](http://uberon.github.io/) — Integrated Cross-Species Anatomy Ontology
- [FBbt](https://github.com/FlyBase/drosophila-anatomy-developmental-ontology) — Drosophila Anatomy Ontology
- [ZFA](https://github.com/cerivs/zebrafish-anatomical-ontology) — Zebrafish Anatomy and Development Ontology
- [EMAPA](https://obofoundry.org/ontology/emapa.html) — Mouse Developmental Anatomy Ontology
- [WBbt](https://github.com/obophenotype/c-elegans-gross-anatomy-ontology) — C. elegans Gross Anatomy Ontology
- [XAO](https://github.com/xenopus-anatomy/xao) — Xenopus Anatomy Ontology
- [CL](https://github.com/obophenotype/cell-ontology) — Cell Ontology
- [DDANAT](https://obofoundry.org/ontology/ddanat.html) — Dictyostelium Anatomy Ontology

### Disease

Disease classification providing the disease hierarchy and disease-phenotype relationships used throughout the Monarch KG.

- [MONDO](https://mondo.monarchinitiative.org/) — Monarch Disease Ontology
- [MPATH](http://www.pathbase.net/Pathology_Ontology/) — Mouse Pathology Ontology

### Procedure

Medical actions and interventions from the Medical Action Ontology.

- [MAXO](https://obofoundry.org/ontology/maxo.html) — Medical Action Ontology

### BiologicalProcess / MolecularActivity / CellularComponent

Gene Ontology terms representing biological processes, molecular functions, and cellular components.

- [GO](http://geneontology.org/) — Gene Ontology

### ChemicalEntity

Chemical entities relevant to phenotype and disease biology.

- [CHEBI](https://www.ebi.ac.uk/chebi/) — Chemical Entities of Biological Interest

### Gene

Gene identifiers used for disease-gene relationships within ontological axioms.

- [HGNC](https://www.genenames.org/) — HUGO Gene Nomenclature Committee
- [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene) — NCBI Gene identifiers

### OrganismTaxon

Taxonomy terms for the model organism species represented in the phenotype ontologies.

- [NCBITaxon](https://www.ncbi.nlm.nih.gov/taxonomy) (slim) — NCBI Taxonomy

### LifeStage

Developmental stage terms used to contextualize phenotype and expression data.

- [HsapDv](https://github.com/obophenotype/developmental-stage-ontologies) — Human Developmental Stages
- [ZFS](https://github.com/cerivs/zebrafish-anatomical-ontology) — Zebrafish Stage Ontology
- [WBls](https://obofoundry.org/ontology/wbls.html) — C. elegans Life Stages
- [FBdv](https://obofoundry.org/ontology/fbdv.html) — Drosophila Developmental Stages

## Edge Types

| Predicate | Description |
|---|---|
| `biolink:subclass_of` | Ontological hierarchy (is-a relationships) |
| `biolink:related_to` | Cross-ontology relationships derived from OWL axioms (part_of, has_part, develops_from, etc.) |
| `biolink:same_as` | Cross-species phenotype equivalences from uPheno SSSOM mappings |
| `biolink:has_phenotype` | Disease-to-phenotype associations from MONDO axioms |
| `biolink:disease_has_location` | Disease anatomical location from MONDO axioms |

## Cross-Species Mappings and Bridges

PHENIO includes bridge axioms and mapping sets that enable cross-species inference:

- **uPHENO bridge axioms** — link species-specific phenotype ontologies to cross-species uPHENO classes
- **uPHENO alignment axioms** — integrate phenotype ontologies across species
- **SSSOM mapping sets** — standardized term mappings from [Uberon](http://purl.obolibrary.org/obo/uberon/uberon.sssom.tsv) (anatomy), [CL](http://purl.obolibrary.org/obo/cl/cl.sssom.tsv) (cell types), and [uPHENO-OBA](https://github.com/obophenotype/upheno) (phenotype-attribute)

## Supporting Ontologies

These ontologies provide relational structure, quality descriptors, and upper-level categories rather than contributing primary nodes:

- [BFO](https://basic-formal-ontology.org/) — Basic Formal Ontology (upper-level categories)
- [RO](http://www.obofoundry.org/ontology/ro.html) — Relations Ontology (relationship types)
- [PATO](http://www.obofoundry.org/ontology/pato.html) — Phenotypic Quality Ontology (qualities used in phenotype definitions)
- [ECO](https://evidenceontology.org/) — Evidence and Conclusion Ontology
- [NBO](http://www.obofoundry.org/ontology/nbo.html) — Neuro Behavior Ontology
- [SO](https://obofoundry.org/ontology/so.html) — Sequence Ontology (sequence features and attributes)
- [Monochrom](https://github.com/monarch-initiative/monochrom) — Chromosome Ontology
- [BSPO](https://obofoundry.org/ontology/bspo.html) — Biological Spatial Ontology (spatial relationships)
- [PR](https://obofoundry.org/ontology/pr.html) — Protein Ontology (slim)

## License

BSD-3-Clause
