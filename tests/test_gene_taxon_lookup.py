"""Tests for build_gene_taxon_lookup sidecar generator."""
import csv
import os
import tempfile
import unittest

from kg_phenio.transform_utils.phenio.phenio_transform import (
    GENE_TAXON_SIDECAR,
    build_gene_taxon_lookup,
)


def _write_tsv(path, header, rows):
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        writer.writerow(header)
        for r in rows:
            writer.writerow(r)


class TestBuildGeneTaxonLookup(unittest.TestCase):
    """Verify the gene_taxon.tsv sidecar contents under various inputs."""

    def _scaffold(self, tmp, edges, nodes, basename="PhenioTransform"):
        _write_tsv(
            os.path.join(tmp, f"{basename}_edges.tsv"),
            ["id", "subject", "predicate", "object", "relation"],
            edges,
        )
        _write_tsv(
            os.path.join(tmp, f"{basename}_nodes.tsv"),
            ["id", "category", "name"],
            nodes,
        )

    def _read_sidecar(self, tmp):
        path = os.path.join(tmp, GENE_TAXON_SIDECAR)
        with open(path, newline="") as fh:
            return list(csv.DictReader(fh, delimiter="\t"))

    def test_extracts_gene_taxon_for_hgnc_and_ncbigene(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold(
                tmp,
                edges=[
                    ["e1", "HGNC:1234", "biolink:in_taxon", "NCBITaxon:9606", "RO:0002162"],
                    ["e2", "NCBIGene:99", "biolink:in_taxon", "NCBITaxon:10090", "RO:0002162"],
                    # Non-gene RO:0002162 subjects (e.g., chromosomes) must be ignored.
                    ["e3", "CHR:9606-chr1", "biolink:in_taxon", "NCBITaxon:9606", "RO:0002162"],
                    # Non-taxon relations must be ignored.
                    ["e4", "HGNC:7777", "biolink:subclass_of", "HGNC:8888", "rdfs:subClassOf"],
                ],
                nodes=[
                    ["NCBITaxon:9606", "biolink:OrganismTaxon", "Homo sapiens"],
                    ["NCBITaxon:10090", "biolink:OrganismTaxon", "Mus musculus"],
                ],
            )
            build_gene_taxon_lookup(tmp)
            rows = {r["gene_id"]: r for r in self._read_sidecar(tmp)}
            self.assertEqual(set(rows.keys()), {"HGNC:1234", "NCBIGene:99"})
            self.assertEqual(rows["HGNC:1234"]["taxon_id"], "NCBITaxon:9606")
            self.assertEqual(rows["HGNC:1234"]["taxon_label"], "Homo sapiens")
            self.assertEqual(rows["NCBIGene:99"]["taxon_id"], "NCBITaxon:10090")
            self.assertEqual(rows["NCBIGene:99"]["taxon_label"], "Mus musculus")

    def test_first_taxon_wins_on_duplicates(self):
        """A gene with multiple taxon edges keeps the first one (stable)."""
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold(
                tmp,
                edges=[
                    ["e1", "HGNC:1", "biolink:in_taxon", "NCBITaxon:9606", "RO:0002162"],
                    ["e2", "HGNC:1", "biolink:in_taxon", "NCBITaxon:10090", "RO:0002162"],
                ],
                nodes=[
                    ["NCBITaxon:9606", "biolink:OrganismTaxon", "Homo sapiens"],
                    ["NCBITaxon:10090", "biolink:OrganismTaxon", "Mus musculus"],
                ],
            )
            build_gene_taxon_lookup(tmp)
            rows = {r["gene_id"]: r for r in self._read_sidecar(tmp)}
            self.assertEqual(rows["HGNC:1"]["taxon_id"], "NCBITaxon:9606")

    def test_missing_taxon_node_yields_blank_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold(
                tmp,
                edges=[
                    ["e1", "HGNC:42", "biolink:in_taxon", "NCBITaxon:99999", "RO:0002162"],
                ],
                nodes=[],
            )
            build_gene_taxon_lookup(tmp)
            rows = {r["gene_id"]: r for r in self._read_sidecar(tmp)}
            self.assertEqual(rows["HGNC:42"]["taxon_id"], "NCBITaxon:99999")
            self.assertEqual(rows["HGNC:42"]["taxon_label"], "")

    def test_no_inputs_no_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            # No PhenioTransform_*.tsv files at all — should log and return cleanly.
            build_gene_taxon_lookup(tmp)
            self.assertFalse(os.path.exists(os.path.join(tmp, GENE_TAXON_SIDECAR)))

    def test_empty_inputs_writes_header_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._scaffold(tmp, edges=[], nodes=[])
            build_gene_taxon_lookup(tmp)
            rows = self._read_sidecar(tmp)
            self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
