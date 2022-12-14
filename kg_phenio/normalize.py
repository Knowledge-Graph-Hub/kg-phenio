"""Call universalizer to normalize graph components."""
from universalizer.norm import clean_and_normalize_graph


def normalize() -> None:
    """Process merged graph with universalizer.

    Args:
        None

    Returns:
        None

    """
    print("Normalizing nodes and categories...")
    clean_and_normalize_graph(filepath="data/merged/",
                              compressed=False,
                              maps=[],
                              update_categories=True,
                              contexts=[],
                              namespace_cat_map="",
                              oak_lookup=False)
    print("Complete.")
