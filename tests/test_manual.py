"""
Manual tests to verify the generated Anki decks.
"""

import os
import pytest
import tarfile
from pathlib import Path

from anki_poker_master.cli import (
    main_with_args,
    EXAMPLE_CONFIG_FILE,
    EXAMPLE_SCENARIO_FILE,
)


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

    num_cards = input("How many cards are in the deck? ")
    assert int(num_cards) == 7

    tags = input(
        "Check one note at random and type the tags here (separated by comma): "
    )
    tags = set(t.lower().strip() for t in tags.split(","))
    assert tags == {"poker", "manual-test"}

    contains_notes = input(
        "Do the cards contain the expected note 'This is a test'? (y/n) "
    )
    assert contains_notes.lower() == "y"

    can_study = input("Can you study the deck? (y/n) ")
    assert can_study.lower() == "y"

    can_you_mark_ranges = input("Can you mark the ranges in the deck? (y/n) ")
    assert can_you_mark_ranges.lower() == "y"

    anything_wrong = input("Is there anything else wrong with the deck? (y/n) ")
    assert anything_wrong.lower() == "n"


def _extract_tar_gz(file_path, destination):
    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall(path=destination)
