"""
Manual tests to verify the generated Anki decks.
"""

import os
import pytest
import tarfile
from pathlib import Path

from anki_poker_master.cli import main_with_args


# The following tests are not run by default, as they require Anki to be installed
# and the user to manually verify the generated decks.
# To run these tests, use the following command:
#     APM_MANUAL_TESTS=true poetry run pytest tests/test_manual.py -s
# and then manually verify the generated decks in the output directory.
@pytest.mark.skipif(
    not os.getenv("APM_MANUAL_TESTS"),
    reason="Skip this test by default, unless APM_MANUAL_TESTS is set",
)
def test_manual_deck_creation(tmp_path):
    (tmp_path / "anki").mkdir()
    scenarios_file = tmp_path / "scenarios.yml"
    scenarios_file.write_text(
        """
- game: NLHE
  position: UTG
  scenario: Top left
  ranges:
    Call: 98+, A8+, K8+, Q8+, J8+, T8+
    Raise: 88+
  notes: This is a test
""".lstrip()
    )
    pkg_path = tmp_path / "AnkiPokerMaster.apkg"

    main_with_args(
        [
            "-s",
            str(scenarios_file),
            "-o",
            str(pkg_path),
            "--tags",
            "poker",
            "manual-test",
        ]
    )
    anki_base_tar = Path(__file__).parent / "anki_base.tar.gz"
    anki_base_path = tmp_path / "anki"
    _extract_tar_gz(anki_base_tar, anki_base_path)

    print("Manually execute the following command:")
    print()
    print(f"    anki -b {tmp_path / 'anki'}")
    print()
    print("Then import the generated deck and verify that it looks correct.")
    print("Path to the generated deck:")
    print()
    print("    " + str(pkg_path))
    print()

    questions = [
        # Browser questions
        ("How many decks are in the package?", "2"),
        (
            "Are the decks named 'AnkiPokerMaster::Standard' and 'AnkiPokerMaster::Detailed' respectively? (y/n)",
            "y",
        ),
        # Browser questions: Standard deck
        ("Standard deck: How many cards are in it?", "32"),
        (
            "Standard deck: Check one note at random and type the tags here (separated by comma):",
            {"poker", "manual-test"},
        ),
        (
            "Standard deck: Check one note at random, does it contain the expected note 'This is a test'? (y/n)",
            "y",
        ),
        # Browser questions: Detailed deck
        ("Detailed deck: How many cards are in there?", "169"),
        (
            "Detailed deck: Check one note at random and type the tags here (separated by comma):",
            {"poker", "manual-test"},
        ),
        (
            "Detailed deck: Check one note at random, does it contain correct images? (y/n)",
            "y",
        ),
        (
            "Detailed deck: Check one note at random, does it contain the expected note 'This is a test'? (y/n)",
            "y",
        ),
        # Studying questions
        ("Standard deck: Can you study it? (y/n)", "y"),
        (
            "Standard deck: Can you mark the ranges on the front but not the back of the cards? (y/n)",
            "y",
        ),
        ("Detailed deck: Can you study it? (y/n)", "y"),
        # Closing questions
        ("Is there anything else wrong with the decks? (y/n)", "n"),
    ]
    wrong_answers = []

    for question, expected_answer in questions:
        answer = input(question + " ")
        if isinstance(expected_answer, set):
            answer = set(s.strip() for s in answer.split(","))
        if answer != expected_answer:
            wrong_answers.append((question, expected_answer, answer))

    def format_wrong_answer(wrong_answer):
        question, expected_answer, answer = wrong_answer
        return f"{question}\nExpected: {expected_answer}\nGot: {answer}\n"

    is_closed = "n"
    while is_closed.lower() != "y":
        print("Please close Anki so the temporary files can be deleted.")
        is_closed = input("Is Anki closed? (y/n) ")

    assert not wrong_answers, "\n" + "\n".join(map(format_wrong_answer, wrong_answers))


def _extract_tar_gz(file_path, destination):
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=destination)
