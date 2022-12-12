# kg-phenio

A graph for accessing and comparing knowledge concerning phenotypes across species and genetic backgrounds.

Also great for ontology-based graph machine learning experiments.

[Please see the repo project for an overview.](https://github.com/Knowledge-Graph-Hub/kg-phenio/projects/1)

See also [OntoML](https://github.com/Knowledge-Graph-Hub/OntoML)
and [Phenio](https://github.com/monarch-initiative/phenio).

## Setup

Clone the repository, then install with `poetry install`.

## Operation

Download sources:

`python run.py download`

Transform sources:

`python run.py transform`

Build the merged graph:

`python run.py merge`

Prepare embeddings and classifiers with NEAT. These are defined in `neat.yaml`.

Or, if running locally, try using `neat_local.yaml`.
