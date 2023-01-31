"""Transform for PHENIO."""
import os
import sys
import tarfile
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore
from koza.cli_runner import transform_source

from kg_phenio.transform_utils.transform import Transform
from kg_phenio.utils.robot_utils import initialize_robot, robot_convert

ONTO_FILES = {
    "PhenioTransform": "phenio.owl",
}

KOZA_CONFIG = "phenio_sources.yaml"

TRANSLATION_TABLE = "./kg_phenio/transform_utils/translation_table.yaml"


class PhenioTransform(Transform):
    """Parse the PHENIO OWL into nodes and edges."""

    def __init__(self, input_dir: str = "", output_dir: str = ""):
        """Set defaults for PHENIO and set up ROBOT."""
        source_name = "phenio"
        super().__init__(source_name, input_dir, output_dir)

        print("Setting up ROBOT...")
        self.robot_path = os.path.join(os.getcwd(), "robot")
        self.robot_params = initialize_robot(self.robot_path)
        print(f"ROBOT path: {self.robot_path}")
        self.robot_env = self.robot_params[1]
        print(f"ROBOT evironment variables: {self.robot_env['ROBOT_JAVA_ARGS']}")

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
            # load all ontologies
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
        if not os.path.exists(data_file):
            if os.path.exists(data_file + ".tar.gz"):
                print(f"Decompressing {data_file}")
                with tarfile.open(data_file) as compfile:
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
        ]
        data_file_tmp = data_file + ".tmp"
        with open(data_file, "r") as infile:
            with open(data_file_tmp, "w") as outfile:
                linenum = 0
                for line in infile:
                    linenum = linenum + 1
                    if line.strip() not in offending_lines:
                        outfile.write(line)
                    else:
                        print(f"Found error at line {linenum}: {line.strip()}.")
        os.replace(data_file_tmp, data_file)

        # Convert to obojson.
        data_file_json = os.path.splitext(data_file)[0] + ".json"

        if not robot_convert(
            robot_path=self.robot_path,
            input_path=data_file,
            output_path=data_file_json,
            robot_env=self.robot_env,
        ):
            sys.exit(f"Failed to convert {data_file}!")

        # Now do that transform to TSV.
        print("Transforming to KGX TSV...")
        transform(
            inputs=[data_file_json],
            input_format="obojson",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
            stream=True
        )

        # Final step in translation:
        # Use Koza to apply additional properties,
        # based on each source
        print(f"Adding sources using {KOZA_CONFIG}")
        transform_source(
            source=KOZA_CONFIG,
            output_dir=self.output_dir,
            output_format="tsv",
            global_table=TRANSLATION_TABLE,
            local_table=None,
        )