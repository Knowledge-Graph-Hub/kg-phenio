"""Test version checker."""
from validate_version_code import validate_version_code

from kg_phenio.__version__ import __version__


def test_version():
    """Tests the package version."""

    assert validate_version_code(__version__)

    return None
