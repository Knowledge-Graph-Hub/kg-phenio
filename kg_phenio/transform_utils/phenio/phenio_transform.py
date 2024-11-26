"""Transform for PHENIO."""

import os
import sys
import tarfile
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore
from koza.cli_utils import transform_source

from kg_phenio.transform_utils.transform import Transform
from kg_phenio.utils.robot_utils import initialize_robot, robot_convert

ONTO_FILES = {
    "PhenioTransform": "phenio.owl",
    "PhenioTransformTest": "phenio-test.owl",
}

KOZA_CONFIGS = {
    "edge": "kg_phenio/transform_utils/phenio/phenio_edge_sources.yaml",
    "node": "kg_phenio/transform_utils/phenio/phenio_node_sources.yaml",
}

TRANSLATION_TABLE = "./kg_phenio/transform_utils/translation_table.yaml"

HEADERLINE_PART1 = '<owl:Ontology rdf:about="http://purl.obolibrary.org/obo/'
HEADERLINE_PART2 = 'phenio-test.owl">\n</owl:Ontology>\n'
HEADERLINE = HEADERLINE_PART1 + HEADERLINE_PART2


class PhenioTransform(Transform):
    """Parse the PHENIO OWL into nodes and edges."""

    def __init__(
        self, input_dir: str = "", output_dir: str = "", config: Optional[str] = None
    ):
        """Set defaults for PHENIO and set up ROBOT."""
        source_name = "phenio"
        super().__init__(source_name, input_dir, output_dir)

        print("Setting up ROBOT...")
        self.robot_path = os.path.join(os.getcwd(), "robot")
        self.robot_params = initialize_robot(self.robot_path)
        print(f"ROBOT path: {self.robot_path}")
        self.robot_env = self.robot_params[1]
        print(f"ROBOT evironment variables: {self.robot_env['ROBOT_JAVA_ARGS']}")

        if config:
            print(f"Have a transform config: {config}")
            self.config = config

            config_name = (config.split("."))[0]
            test_config = f"{config_name}-test.yaml"
            print(f"Have a test transform config: {test_config}")
            self.test_config = test_config

    def run(self, data_file: Optional[str] = None) -> None:
        """Call transform and perform it.

        Args:
            data_file: data file to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split(".")[0]
            data_file = os.path.join(self.input_base_dir, data_file)
            self.parse(k, data_file, k)
        else:
            # Load PHENIO
            for k in ONTO_FILES.keys():
                data_file = os.path.join(self.input_base_dir, ONTO_FILES[k])
                self.parse(k, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Process the data_file.

        Args:
            name: Name of the ontology
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """
        # Check if it needs to be decompressed first,
        # and it probably does.
        if not os.path.exists(data_file):
            if os.path.exists(data_file + ".tar.gz"):
                comp_data_file = data_file + ".tar.gz"
                print(f"Decompressing {comp_data_file}")
                with tarfile.open(comp_data_file) as compfile:
                    compfile.extractall(self.input_base_dir)
        else:
            print(f"Found ontology at {data_file}")

        # Check validity of owl before transforming.
        # Repair errors if the repair doesn't remove
        # information (i.e., no node or edge loss).
        # This is necessary for PHENIO because it's large
        # and may contain errors impacting transform to
        # nodes/edges.
        # For now, this means removing empty synonyms, xrefs, and comments.
        print("Checking for errors...")
        offending_lines = [
            "<oboInOwl:hasNarrowSynonym></oboInOwl:hasNarrowSynonym>",
            "<oboInOwl:hasBroadSynonym></oboInOwl:hasBroadSynonym>",
            "<oboInOwl:hasExactSynonym></oboInOwl:hasExactSynonym>",
            "<oboInOwl:hasRelatedSynonym></oboInOwl:hasRelatedSynonym>",
            "<oboInOwl:hasDbXref></oboInOwl:hasDbXref>",
            "<rdfs:comment></rdfs:comment>",
            "<Ontology/>",
        ]
        data_file_tmp = data_file + ".tmp"
        with open(data_file, "r") as infile:
            with open(data_file_tmp, "w") as outfile:
                linenum = 0
                for line in infile:
                    linenum = linenum + 1
                    if line.strip() not in offending_lines:
                        outfile.write(line)
                    elif line.strip() == "<Ontology/>":
                        print(f"Repairing header at line {linenum}.")
                        outfile.write(HEADERLINE)
                    else:
                        print(f"Found error at line {linenum}: {line.strip()}.")
        os.replace(data_file_tmp, data_file)

        # Convert to obojson, if necessary
        data_file_json = os.path.splitext(data_file)[0] + ".json"

        if not os.path.exists(data_file_json):
            if not robot_convert(
                robot_path=self.robot_path,
                input_path=data_file,
                output_path=data_file_json,
                robot_env=self.robot_env,
            ):
                sys.exit(f"Failed to convert {data_file}!")
        else:
            print(f"Found JSON ontology at {data_file_json}.")

        # Now do that transform to TSV, if necessary
        # This is where the KGX config file is used, if provided
        # Note that the config-based transform will transform
        # both the main ontology and the test set.
        data_file_tsv = os.path.join(self.output_dir, name + "_edges.tsv")

        if not os.path.exists(data_file_tsv):
            if self.config:
                if name == "PhenioTransformTest":
                    print(
                        f"Transforming to KGX TSV with test config in {self.test_config}..."
                    )
                    tx_config = self.test_config
                else:
                    print(f"Transforming to KGX TSV with config in {self.config}...")
                    tx_config = self.config
                transform(
                    inputs=None,
                    transform_config=tx_config,
                )
            else:
                print("Transforming to KGX TSV...")
                transform(
                    inputs=[data_file_json],
                    input_format="obojson",
                    output=os.path.join(self.output_dir, name),
                    output_format="tsv",
                    stream=False,
                )
        else:
            print(f"Found KGX TSV edges at {data_file_tsv}.")

        # For the test file, expand the header to match the main ontology
        if name == "PhenioTransformTest":
            print("Completed transform of test file.")
        else:
            # Final step in translation:
            # Use Koza to apply additional properties,
            # based on each source.
            # This is not done for the test file
            # as it is not as detailed as the main ontology.
            for config_type in ["node", "edge"]:
                config = KOZA_CONFIGS[config_type]
                print(f"Adding {config_type} sources using {config}")
                transform_source(
                    source=config,
                    output_dir=self.output_dir,
                    output_format="tsv",
                    global_table=TRANSLATION_TABLE,
                    local_table=None,
                )
