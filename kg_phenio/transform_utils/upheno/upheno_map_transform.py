"""Process Upheno maps."""

import os
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_phenio.transform_utils.transform import Transform

UPHENO_SOURCES = {
    "UPHENO_ALL": "upheno_mapping_all.csv",
}

UPHENO_CONFIGS = {
    "UPHENO_ALL": "upheno_mapping_all.yaml",
}

TRANSLATION_TABLE = "./kg_phenio/transform_utils/translation_table.yaml"


class UphenoMapTransform(Transform):
    """Ingest the table of all Upheno mappings by species.

    It is transformed to KGX nodes/edges.
    This could also handle other similar mappings, e.g., from
    https://github.com/mapping-commons/mh_mapping_initiative/tree/master/mappings
    though those are already in SSSOM format so they would
    require less processing.
    """

    def __init__(self, input_dir: str = "", output_dir: str = "") -> None:
        """Initialize the default source name."""
        source_name = "upheno_mapping"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, upheno_file: Optional[str] = None) -> None:  # type: ignore
        """Set up the Upheno mapping for Koza and call the parse function."""
        if upheno_file:
            for source in [upheno_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in UPHENO_SOURCES.keys():
                name = UPHENO_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Transform Upheno file with Koza."""
        print(f"Parsing {data_file}")
        config = os.path.join(
            "kg_phenio/transform_utils/upheno/", UPHENO_CONFIGS[source]
        )
        output = self.output_dir

        # If source is unknown then we aren't going to guess
        if source not in UPHENO_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")
        else:
            print(f"Transforming using source in {config}")
            transform_source(
                source=config,
                output_dir=output,
                output_format="tsv",
                global_table=TRANSLATION_TABLE,
                local_table=None,
            )
