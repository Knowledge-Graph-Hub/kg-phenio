# kg-ontoml

A graph for machine learning experiments on ontologies.

[Please see the repo project for an overview.](https://github.com/Knowledge-Graph-Hub/kg-ontoml/projects/1)

See also [OntoML](https://github.com/Knowledge-Graph-Hub/OntoML).

## Setup

Clone the repository, then install with `pip install .`

## Operation

Download sources:

`python run.py download`

Transform sources:

`python run.py transform`

Build the merged graph:

`python run.py merge`

Prepare embeddings and classifiers with NEAT. These are defined in `neat.yaml`.

Or, if running locally, try using `neat_local.yaml`.
