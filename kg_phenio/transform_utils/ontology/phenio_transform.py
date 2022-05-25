import os
import tarfile
from typing import Optional
from kg_phenio.transform_utils.transform import Transform
from kg_phenio.utils.transform_utils import remove_obsoletes
from kg_phenio.utils.robot_utils import initialize_robot, relax_ontology, robot_convert
from kg_phenio.query import run_remote_query, parse_query_rq
from kgx.cli.cli_utils import transform # type: ignore

ONTO_FILES = {
    'PhenioTransform': 'phenio-base.owl.tar.gz',
}

QUERY_PATH = 'kg_phenio/transform_utils/ontology/subq_construct.rq'

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

        outname = os.path.basename(data_file[:-7])
        outname_path = os.path.join(self.output_dir, outname)
        if not os.path.exists(outname_path):
            print(f"Decompressing {data_file}")
            with tarfile.open(data_file) as compfile:
                compfile.extractall(self.output_dir)
        else:
            print(f"Found decompressed ontology at {outname_path}")

        print(f"Parsing {outname}")

        relaxed_outpath = os.path.join(self.output_dir,outname+"_relaxed.owl")
        if not os.path.exists(relaxed_outpath):
            print(f"ROBOT: relax {outname_path}")
            if not relax_ontology(self.robot_path, 
                                outname_path,
                                relaxed_outpath,
                                self.robot_env):
                print(f"Encountered error during robot relax of {source}.")
        else:
            print(f"Found relaxed ontology at {relaxed_outpath}")

        # SPARQL for subq's
        query = parse_query_rq(QUERY_PATH)
        print(query)
        import sys
        sys.exit("testing")

        pregraph_outpath = os.path.join(self.output_dir,outname+"_with-subqs.json")
        if not robot_convert(self.robot_path, 
                                relaxed_outpath,
                                pregraph_outpath,
                                self.robot_env):
            print(f"Encountered error during robot convert of {source}.")

        transform(inputs=[pregraph_outpath], 
                    input_format='owl',
                    output= os.path.join(self.output_dir, name), 
                    output_format='tsv',
                    stream=True)

        remove_obsoletes(os.path.join(self.output_dir, name + "_nodes.tsv"),
                        os.path.join(self.output_dir, name + "_edges.tsv"))

