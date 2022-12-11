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
    clean_and_normalize_graph(input_path="data/merged/",
                              compressed=False,
                              maps=[],
                              update_categories=True,
                              oak_lookup=False)
    print("Complete.")
