"""Transform for PHENIO."""

import csv
import os
import sys
import tarfile
from typing import Optional

import pandas
from kgx.cli.cli_utils import transform  # type: ignore
from koza.cli_utils import transform_source

from kg_phenio.transform_utils.transform import Transform
from kg_phenio.utils.robot_utils import initialize_robot, robot_convert

# Phenio expresses gene→taxon as an OWL existential restriction
# (?gene rdfs:subClassOf [owl:onProperty RO:0002162 ; owl:someValuesFrom ?taxon]),
# which KGX serializes as a separate edge with relation "RO:0002162".
# We want taxon as a node property, so we fold those edges into the gene rows
# before the Koza enrichment runs.
TAXON_RELATION = "RO:0002162"
# Match gene subjects in either CURIE form (after KGX prefix-map contraction)
# or URI form (older KGX or unrecognized prefix).
GENE_ID_PREFIXES = (
    "HGNC:",
    "NCBIGene:",
    "http://identifiers.org/hgnc/",
    "http://identifiers.org/ncbigene/",
)


def materialize_gene_taxon(output_dir: str, basename: str = "PhenioTransform") -> None:
    """Fold gene→taxon edges into in_taxon/in_taxon_label node properties.

    Reads ``{basename}_nodes.tsv`` and ``{basename}_edges.tsv`` in ``output_dir``,
    rewrites both. The ``in_taxon`` and ``in_taxon_label`` columns are added to
    the nodes file unconditionally (downstream Koza configs declare them, so
    they need to be present in the header even when no gene rows have a value).
    """
    nodes_path = os.path.join(output_dir, f"{basename}_nodes.tsv")
    edges_path = os.path.join(output_dir, f"{basename}_edges.tsv")
    if not (os.path.exists(nodes_path) and os.path.exists(edges_path)):
        print(f"materialize_gene_taxon: skipping; missing {nodes_path} or {edges_path}")
        return

    edges = pandas.read_csv(
        edges_path, sep="\t", dtype="string", quoting=csv.QUOTE_NONE, lineterminator="\n"
    )
    is_taxon_edge = edges["relation"].eq(TAXON_RELATION) & edges["subject"].str.startswith(
        GENE_ID_PREFIXES, na=False
    )
    taxon_edges = edges.loc[is_taxon_edge, ["subject", "object"]].drop_duplicates(
        subset=["subject"]
    )
    taxon_by_gene = dict(
        zip(taxon_edges["subject"], taxon_edges["object"], strict=False)
    )

    nodes = pandas.read_csv(
        nodes_path, sep="\t", dtype="string", quoting=csv.QUOTE_NONE, lineterminator="\n"
    )
    is_taxon_node = nodes["id"].str.startswith("NCBITaxon:", na=False)
    label_by_taxon = dict(
        zip(
            nodes.loc[is_taxon_node, "id"],
            nodes.loc[is_taxon_node, "name"],
            strict=False,
        )
    )

    # Always create the columns (Koza yaml expects them); .map yields NaN for
    # nodes that aren't gene rows or have no taxon edge, which serializes as empty.
    nodes["in_taxon"] = nodes["id"].map(taxon_by_gene)
    nodes["in_taxon_label"] = nodes["in_taxon"].map(label_by_taxon)

    populated = int(nodes["in_taxon"].notna().sum())
    labeled = int(nodes["in_taxon_label"].notna().sum())
    print(
        f"materialize_gene_taxon: found {len(taxon_edges)} gene→taxon edges; "
        f"populated in_taxon on {populated} nodes ({labeled} with in_taxon_label)"
    )

    nodes.to_csv(nodes_path, sep="\t", index=False)
    edges.loc[~is_taxon_edge].to_csv(edges_path, sep="\t", index=False)

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
        data_file_json = os.path.splitext(data_file)[0] + ".json"
        have_json = False

        # Check if it needs to be decompressed first,
        # and it probably does.
        if not os.path.exists(data_file) and not os.path.exists(data_file_json):
            if os.path.exists(data_file + ".tar.gz"):
                comp_data_file = data_file + ".tar.gz"
            elif os.path.exists(data_file + ".gz"):
                comp_data_file = data_file + ".gz"
            else:
                sys.exit("Cannot find ontology file! Exiting...")
            print(f"Decompressing {comp_data_file}")
            with tarfile.open(comp_data_file) as compfile:
                compfile.extractall(self.input_base_dir)
        elif os.path.exists(data_file_json):
            print(f"Found obojson ontology at {data_file_json}.")
            have_json = True
        else:
            print(f"Found ontology at {data_file}")

        # Check validity of owl before transforming.
        # Repair errors if the repair doesn't remove
        # information (i.e., no node or edge loss).
        # This is necessary for PHENIO because it's large
        # and may contain errors impacting transform to
        # nodes/edges.
        # For now, this means removing empty synonyms, xrefs, and comments.
        if not have_json:
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
            if not robot_convert(
                robot_path=self.robot_path,
                input_path=data_file,
                output_path=data_file_json,
                robot_env=self.robot_env,
            ):
                sys.exit(f"Failed to convert {data_file}!")

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
            # Fold <gene> RO:0002162 <taxon> edges into in_taxon/in_taxon_label
            # columns on the gene rows so the Koza enrichment sees taxon as a
            # node property rather than as a separate edge.
            print("Materializing gene→taxon edges as node properties...")
            materialize_gene_taxon(self.output_dir, basename=name)

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
