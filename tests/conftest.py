import os
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        help="Update the golden files",
        default=False,
    )


@pytest.fixture
def golden_dir(request):
    golden_dir_path = os.path.join(
        os.path.dirname(__file__),
        "golden",
        request.node.module.__name__.split(".")[-1],
        request.node.function.__name__,
    )
    if not os.path.exists(golden_dir_path):
        os.makedirs(golden_dir_path)
    return golden_dir_path
