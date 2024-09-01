import os
import pytest

from anki_poker_master.model.hand import Street


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden",
        action="store_true",
        help="Update the golden files",
        default=False,
    )


@pytest.fixture
def golden_dir(request):
    modules = request.node.module.__name__.split(".")[1:]  # excluding initial "tests"
    golden_dir_path = os.path.join(
        os.path.dirname(__file__),
        *modules[:-1],
        "golden",
        modules[-1],
        request.node.function.__name__,
    )
    if not os.path.exists(golden_dir_path):
        os.makedirs(golden_dir_path)
    return golden_dir_path


@pytest.fixture
def testdata_dir(request):
    modules = request.node.module.__name__.split(".")[1:]  # excluding initial "tests"
    testdata_dir_path = os.path.join(
        os.path.dirname(__file__),
        *modules[:-1],
        "testdata",
        modules[-1],
        request.node.function.__name__,
    )
    if not os.path.exists(testdata_dir_path):
        os.makedirs(testdata_dir_path)
    return testdata_dir_path


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, Street) and isinstance(right, Street) and op == "==":
        return [
            "Comparing Street instances:",
            "      LEFT   |   RIGHT",
            f"  name: {left.name}   |   {right.name}",
            f"  board: {left.board}   |   {right.board}",
            f"  initial_pots: {left.initial_pots}   |   {right.initial_pots}",
            f"  initial_players: {left.initial_players}   |   {right.initial_players}",
            f"  initial_stacks: {left.initial_stacks}   |   {right.initial_stacks}",
            f"  first_player: {left.first_player}   |   {right.first_player}",
            f"  actions: {left.actions}   |   {right.actions}",
            f"  questions: {left.questions}   |   {right.questions}",
            f"  default_questions: {left.default_questions}   |   {right.default_questions}",
        ]
