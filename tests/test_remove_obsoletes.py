import unittest
import os
from kg_phenio.utils.transform_utils import remove_obsoletes

class TestRemoveObsoletes(unittest.TestCase):

    def setUp(self) -> None:
        self.nodepath = "tests/resources/graph_with_obs_nodes.tsv"
        self.edgepath = "tests/resources/graph_with_obs_edges.tsv"

    def test_remove_obsolete_nodes_and_edges(self):
        pre_node_size = os.path.getsize(self.nodepath)
        pre_edge_size = os.path.getsize(self.edgepath)

        remove_obsoletes(self.nodepath, self.edgepath)

        post_node_size = os.path.getsize(self.nodepath)
        post_edge_size = os.path.getsize(self.edgepath)

        self.assertLess(post_node_size, pre_node_size)
        self.assertLess(post_edge_size, pre_edge_size)
