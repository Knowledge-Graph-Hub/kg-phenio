"""Utilities for loading the config YAML for merging."""
from typing import Dict

import networkx as nx
import yaml
from kgx.cli.cli_utils import merge


def parse_load_config(yaml_file: str) -> Dict:
    """Parse load config YAML.

    Args:
        yaml_file: A string pointing to a KGX compatible config YAML.

    Returns:
        Dict: The config as a dictionary.

    """
    with open(yaml_file) as yml:
        config = yaml.load(yml, Loader=yaml.FullLoader)
    return config


def load_and_merge(yaml_file: str, processes: int = 1) -> nx.MultiDiGraph:
    """Load and merge sources defined in the config YAML.

    Args:
        yaml_file: A string pointing to a KGX compatible config YAML.
        processes: Number of processes to use.

    Returns:
        networkx.MultiDiGraph: The merged graph.

    """
    merged_graph = merge(yaml_file, processes=processes)

    return merged_graph
