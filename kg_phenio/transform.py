"""Run transforms defined by transform_utils."""
import logging
from typing import List

from kg_phenio.transform_utils.phenio.phenio_transform import PhenioTransform
from kg_phenio.transform_utils.upheno.upheno_map_transform import \
    UphenoMapTransform

DATA_SOURCES = {
    "PhenioTransform": PhenioTransform,
    "UphenoMapTransform": UphenoMapTransform,
}


def transform(
    input_dir: str, output_dir: str, sources: List[str]
) -> None:
    """Call scripts in kg_phenio/transform/[source name]/ to transform each source.

    Args:
        input_dir: A string pointing to the directory to import data from.
        output_dir: A string pointing to the directory to output data to.
        sources: A list of sources to transform.
    Returns:
        None.
    """
    if not sources:
        # run all sources
        sources = list(DATA_SOURCES.keys())

    for source in sources:
        if source in DATA_SOURCES:
            logging.info(f"Parsing {source}")
            t = DATA_SOURCES[source](input_dir, output_dir)
            t.run()
