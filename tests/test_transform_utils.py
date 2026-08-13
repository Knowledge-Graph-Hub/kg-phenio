"""Test the category and CURIE parser utils."""
import unittest

from parameterized import parameterized

from kg_phenio.transform_utils.sources import NODE_SOURCES
from kg_phenio.utils.transform_utils import (
    collapse_uniprot_curie,
    guess_bl_category,
    split_generic_obo_curie,
)


class TestTransformUtils(unittest.TestCase):
    """Test class for transform utils."""

    @parameterized.expand(
        [
            ["", "biolink:NamedThing"],
            ["UniProtKB", "biolink:Protein"],
            ["ComplexPortal", "biolink:Protein"],
            ["GO", "biolink:OntologyClass"],
        ]
    )
    def test_guess_bl_category(self, curie, category):
        """Test guessing Biolink category."""
        self.assertEqual(category, guess_bl_category(curie))

    @parameterized.expand(
        [
            ["foobar", "foobar"],
            ["ENSEMBL:ENSG00000178607", "ENSEMBL:ENSG00000178607"],
            ["UniprotKB:P63151-1", "UniprotKB:P63151"],
            ["uniprotkb:P63151-1", "uniprotkb:P63151"],
            ["UniprotKB:P63151-2", "UniprotKB:P63151"],
        ]
    )
    def test_collapse_uniprot_curie(self, curie, collapsed_curie):
        """Test collapsing Uniprot protein CURIEs."""
        self.assertEqual(collapsed_curie, collapse_uniprot_curie(curie))


class TestGenericOboCurie(unittest.TestCase):
    """Test recovery of idspaces from CURIEs collapsed onto the generic OBO prefix."""

    @parameterized.expand(
        [
            # Splittable: <idspace>_<localid>, with the idspace's case preserved.
            ["OBO", "DDPHENO_0000001", "DDPHENO", "0000001"],
            ["OBO", "FBbt_00000001", "FBbt", "00000001"],
            ["OBO", "HsapDv_0000001", "HsapDv", "0000001"],
            # Not splittable: these keep the generic OBO prefix.
            ["OBO", "FBbt_root_00000000", "OBO", "FBbt_root_00000000"],
            ["OBO", "fbbt#has_function_in", "OBO", "fbbt#has_function_in"],
            ["OBO", "go/extensions/ro_0002092", "OBO", "go/extensions/ro_0002092"],
            ["OBO", "ObsoleteClass", "OBO", "ObsoleteClass"],
            # Every other prefix passes through untouched.
            ["FYPO", "0000001", "FYPO", "0000001"],
            ["HGNC", "1234", "HGNC", "1234"],
        ]
    )
    def test_split_generic_obo_curie(self, prefix, local_id, exp_prefix, exp_local_id):
        """Test splitting a generic OBO CURIE into its real idspace."""
        self.assertEqual((exp_prefix, exp_local_id), split_generic_obo_curie(prefix, local_id))

    @parameterized.expand(
        [
            ["OBO:DDPHENO_0000001", "PhenotypicFeature"],
            ["OBO:FBbt_00000001", "AnatomicalEntity"],
            ["OBO:WBbt_0005733", "AnatomicalEntity"],
            ["OBO:EMAPA_16040", "AnatomicalEntity"],
            ["OBO:ZFA_0000001", "AnatomicalEntity"],
            ["OBO:XAO_0000001", "AnatomicalEntity"],
            ["OBO:ZFS_0000001", "LifeStage"],
            ["OBO:CHR_0000001", "MolecularEntity"],
            ["OBO:XPO_0000001", "PhenotypicFeature"],
            ["OBO:HsapDv_0000001", "LifeStage"],
        ]
    )
    def test_node_category_found_by_idspace(self, curie, category):
        """Test that a node category is reachable when kgx collapses the prefix.

        kgx contracts OBO ontologies missing from its prefix map to
        OBO:<idspace>_<localid>. NODE_SOURCES has no category under "OBO", so
        without the split these nodes keep the generic biolink:NamedThing --
        which is what left ~52k phenio nodes untyped from kg-phenio 20260603 on.
        """
        prefix, local_id = curie.split(":", 1)
        prefix, _ = split_generic_obo_curie(prefix, local_id)
        self.assertEqual(category, NODE_SOURCES[prefix][1])
