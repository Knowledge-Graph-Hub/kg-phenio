"""Test functions for removing obsolete nodes/edges."""
import os
import unittest

from kg_phenio.utils.transform_utils import remove_obsoletes


class TestRemoveObsoletes(unittest.TestCase):
    def setUp(self) -> None:
        self.nodepath = "tests/resources/graph_with_obs_nodes.tsv"
        self.edgepath = "tests/resources/graph_with_obs_edges.tsv"
        self.partnodepath = "tests/resources/graph_with_obs_part_nodes.tsv"
        self.partedgepath = "tests/resources/graph_with_obs_part_edges.tsv"

    def test_remove_obsolete_nodes_and_edges(self):
        pre_node_size = os.path.getsize(self.nodepath)
        pre_edge_size = os.path.getsize(self.edgepath)

        remove_obsoletes(self.nodepath, self.edgepath)

        post_node_size = os.path.getsize(self.nodepath)
        post_edge_size = os.path.getsize(self.edgepath)

        self.assertLess(post_node_size, pre_node_size)
        self.assertLess(post_edge_size, pre_edge_size)

    def test_remove_obsolete_participant_nodes_and_edges(self):
        pre_node_size = os.path.getsize(self.partnodepath)
        pre_edge_size = os.path.getsize(self.partedgepath)

        remove_obsoletes(self.partnodepath, self.partedgepath)

        post_node_size = os.path.getsize(self.partnodepath)
        post_edge_size = os.path.getsize(self.partedgepath)

        self.assertLess(post_node_size, pre_node_size)
        self.assertLess(post_edge_size, pre_edge_size)
