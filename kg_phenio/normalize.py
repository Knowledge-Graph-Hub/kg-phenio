"""Call universalizer to normalize graph components."""
from universalizer.norm import clean_and_normalize_graph


def normalize() -> None:
    """Process merged graph with universalizer.

    Args:
        None

    Returns:
        None

    """
    # Use the Monarch-specific `merged.monarch` context from prefixmaps as
    # the single source of CURIE↔IRI conventions. The previous
    # `["obo", "bioregistry.upper"]` pair interacted with universalizer's
    # lowercased-reverse-IRI logic in `make_id_maps` and was producing
    # all-uppercase prefix casings for OBO mixed-case anatomies (FBbt →
    # FBBT, WBbt → WBBT). That dropped ~503k Drosophila + C. elegans
    # gene-expression edges to dangling in the 2026-06-03 monarch-kg build
    # (the entire shortfall on `alliance_gene_to_expression_edges`).
    # `merged.monarch` is also what monarch-app's `curie_service.py` uses,
    # so the whole stack is now aligned.
    print("Normalizing nodes and categories...")
    clean_and_normalize_graph(
        filepath="data/merged/",
        compressed=False,
        maps=[],
        update_categories=True,
        contexts=["merged.monarch"],
        namespace_cat_map="",
        oak_lookup=False,
    )
    print("Complete.")
