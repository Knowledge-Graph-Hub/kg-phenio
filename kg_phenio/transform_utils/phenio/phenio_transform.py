import os
import sys
import tarfile
from typing import Optional

from kg_phenio.transform_utils.transform import Transform
from kg_phenio.utils.transform_utils import remove_obsoletes
from kg_phenio.utils.robot_utils import initialize_robot, relax_ontology, robot_query_construct, robot_query_update
from kgx.cli.cli_utils import transform # type: ignore

ONTO_FILES = {
    'PhenioTransform': 'phenio.owl',
}

QUERY_PATH = 'kg_phenio/transform_utils/phenio/subq_construct.sparql'

class PhenioTransform(Transform):
    """
    PhenioTransform parses the phenio OWL into nodes and edges.
    """
    def __init__(self, input_dir: str = None, output_dir: str = None):
        source_name = "phenio"
        super().__init__(source_name, input_dir, output_dir)

        print("Setting up ROBOT...")
        self.robot_path = os.path.join(os.getcwd(),"robot")
        self.robot_params = initialize_robot(self.robot_path)
        print(f"ROBOT path: {self.robot_path}")
        self.robot_env = self.robot_params[1]
        print(f"ROBOT evironment variables: {self.robot_env['ROBOT_JAVA_ARGS']}")

    def run(self, data_file: Optional[str] = None) -> None:
        """Method is called and performs needed transformations to process
        an ontology.
        Args:
            data_file: data file to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split('.')[0]
            data_file = os.path.join(self.input_base_dir, data_file)
            self.parse(k, data_file, k)
        else:
            # load all ontologies
            for k in ONTO_FILES.keys():
                data_file = os.path.join(self.input_base_dir, ONTO_FILES[k])
                self.parse(k, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Processes the data_file.
        Once complete, also removes obsolete classes.
        Args:
            name: Name of the ontology
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """

        if not os.path.exists(data_file):
            if os.path.exists(data_file+".tar.gz"):
                print(f"Decompressing {data_file}")
                with tarfile.open(data_file) as compfile:
                    compfile.extractall(self.input_base_dir)
        else:
            print(f"Found ontology at {data_file}")

        print(f"Parsing {data_file}")

        data_filename = os.path.basename(data_file)

        relaxed_outpath = os.path.join(self.output_dir,data_filename[:-4]+"_relaxed.owl")
        if not os.path.exists(relaxed_outpath):
            print(f"ROBOT: relax {data_file}")
            if not relax_ontology(self.robot_path, 
                                data_file,
                                relaxed_outpath,
                                self.robot_env):
                print(f"Encountered error during robot relax of {source}.")
                sys.exit("Cannot continue. Exiting...")
        else:
            print(f"Found relaxed ontology at {relaxed_outpath}")

        # SPARQL for subq's
        subq_outpath = relaxed_outpath[:-4]+"_subqs.owl"
        query_result_path = relaxed_outpath[:-4]+"_subqs_queryresult.owl"
        if not os.path.exists(subq_outpath):
            if not robot_query_construct(self.robot_path,
                                        relaxed_outpath,
                                        QUERY_PATH,
                                        query_result_path,
                                        self.robot_env):
                print(f"Encountered error during robot query construct of {source}.")
                sys.exit("Cannot continue. Exiting...")
            else:
                print("Updating data with query results...")

                # Create the update query first
                query_result_as_insert = "data/transformed/phenio/subq_update.sparql"
                with open(query_result_as_insert, 'w') as updatefile:
                    with open(QUERY_PATH, 'r') as orig_query:
                        for line in orig_query:
                            if line.startswith("PREFIX"):
                                updatefile.write(line)
                    updatefile.write("INSERT DATA\n{\n")
                    with open(query_result_path, 'r') as result:
                        for line in result:
                            if not line.startswith("@prefix"):
                                updatefile.write(line)
                    updatefile.write("}")

                if not robot_query_update(self.robot_path,
                                        relaxed_outpath,
                                        query_result_as_insert,
                                        subq_outpath,
                                        True,
                                        self.robot_env):
                    print(f"Encountered error during robot query update of {source}.")
                    sys.exit("Cannot continue. Exiting...")
                else:
                    print(f"Completed update with subq relations.")
        else:
            print(f"Found relaxed ontology with subqs relations at {subq_outpath}")
        
        transform(inputs=[subq_outpath], 
                    input_format='owl',
                    output= os.path.join(self.output_dir, name), 
                    output_format='tsv',
                    stream=True)

        # remove_obsoletes(os.path.join(self.output_dir, name + "_nodes.tsv"),
        #                os.path.join(self.output_dir, name + "_edges.tsv"))

