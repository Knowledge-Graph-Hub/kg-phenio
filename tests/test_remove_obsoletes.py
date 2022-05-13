import unittest
from kg_phenio.utils.transform_utils import remove_obsoletes

class TestRemoveObsoletes(unittest.TestCase):

    def setUp(self) -> None:
        self.nodepath = "tests/resources/graph_with_obs_nodes.tsv"
        self.edgepath = "tests/resources/graph_with_obs_edges.tsv"

    def test_remove_obsolete_nodes_and_edges(self):
        remove_obsoletes(self.nodepath, self.edgepath)