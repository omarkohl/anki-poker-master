"""
Test the 'hand' subcommand.
"""

from pathlib import Path
from typing import List

import anki
import anki.importing.apkg
from anki.collection import ImportAnkiPackageOptions, ImportAnkiPackageRequest

from tests.utils import compare_or_update_golden, compare_or_update_golden_with_path


def _create_html_content(content, dark_mode=False):
    """
    Helper function to create a full HTML document with the given content. It
    makes it easier to visually inspect the HTML output.
    """
    header = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
"""
    if dark_mode:
        return (
                header
                + '<body style="background-color: #221e1e">\n'
                + '<div class="nightMode">\n'
                + content
                + "</div>\n"
                + "</body>\n"
                + "</html>\n"
        )
    else:
        return header + "<body>\n" + content + "</body>\n" + "</html>\n"


def _create_anki_collection(
        phh_content: str,
        tags: List[str],
        tmp_path: Path,
) -> anki.collection.Collection:
    """
    Create an Anki collection from the given phh content and tags.
    """
    from anki_poker_master.cli import main_with_args

    phh_f = tmp_path / "hand.phh"
    phh_f.write_text(phh_content, encoding="utf-8")

    collection = anki.collection.Collection(str(tmp_path / "collection.anki2"))
    pkg_f = tmp_path / "package.apkg"

    main_with_args(
        [
            "hand",
            *[f"--tag={tag}" for tag in tags],
            "-o",
            str(pkg_f),
            str(phh_f),
        ]
    )

    collection.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(pkg_f),
            options=ImportAnkiPackageOptions(
                with_scheduling=True, with_deck_configs=True
            ),
        )
    )
    return collection


def test_pure_phh_file(pytestconfig, golden_dir, tmp_path):
    """
    Verify that when calling anki-poker-master with a "normal" phh file an
    Anki deck is generated and contains the notes, cards, tags etc. we expect.
    """

    phh_content = """variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 ????",
    "p3 cbr 12",
    "p1 f",
    "p2 cc",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc",
    "d db 4s",
    "p2 cc",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388",
    "p3 f",
]
"""

    collection = _create_anki_collection(phh_content, ["poker"], tmp_path)

    assert collection.tags.all() == ["poker"]
    assert len(collection.decks.all_names_and_ids()) == 3
    deck_id = collection.decks.id_for_name("AnkiPokerMaster::HandHistory")
    assert deck_id
    all_notes_ids = collection.find_notes("")
    assert len(all_notes_ids) == 1

    for note in [collection.get_note(nid) for nid in all_notes_ids]:
        assert len(note.fields) == 47

    all_card_ids = collection.find_cards("")

    assert len(all_card_ids) == 5

    # We know that there is only one note, so we can sort the cards by their
    # 'ord' i.e. which template they use
    sorted_cards = sorted(
        (collection.get_card(cid) for cid in all_card_ids),
        key=lambda c: c.ord,
    )

    # assert that there are no duplicates, just in case, otherwise
    # the golden file comparison below will no longer be deterministic
    assert len(set(card.ord for card in sorted_cards)) == 5

    for card in sorted_cards:
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"answer_{card.ord:02}.html",
            _create_html_content(card.answer()),
        )
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"question_{card.ord:02}.html",
            _create_html_content(card.question()),
        )

    all_media_files = list(Path(collection.media.dir()).rglob("*"))

    expected_media_files = [
        "apm-card-small-4s.png",
        "apm-card-small-8c.png",
        "apm-card-small-8h.png",
        "apm-card-small-Ah.png",
        "apm-card-small-Tc.png",
        "apm-card-small-Th.png",
        "apm-card-small-Ts.png",
    ]

    assert sorted([f.name for f in all_media_files]) == sorted(expected_media_files)

    for f in expected_media_files:
        compare_or_update_golden_with_path(
            pytestconfig,
            golden_dir / f,
            Path(collection.media.dir()) / f,
        )


def test_full_phh_file(testdata_dir, pytestconfig, golden_dir, tmp_path):
    """
    Verify that when calling anki-poker-master with a "full" phh file an
    Anki deck is generated and contains the notes, cards, tags etc. we expect.
    """

    phh_content = (testdata_dir / "harrington-cash-10-13.phh").read_text()

    collection = _create_anki_collection(phh_content, ["poker"], tmp_path)

    assert collection.tags.all() == ["poker"]

    assert len(collection.decks.all_names_and_ids()) == 3

    # We know that there is only one note, so we can sort the cards by their
    # 'ord' i.e. which template they use
    sorted_cards = sorted(
        (collection.get_card(cid) for cid in collection.find_cards("")),
        key=lambda c: c.ord,
    )

    # assert that there are no duplicates, just in case, otherwise
    # the golden file comparison below will no longer be deterministic
    assert len(set(card.ord for card in sorted_cards)) == 5

    for card in sorted_cards:
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"answer_{card.ord:02}.html",
            _create_html_content(card.answer()),
        )
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"question_{card.ord:02}.html",
            _create_html_content(card.question()),
        )

    all_media_files = list(Path(collection.media.dir()).rglob("*"))

    expected_media_files = [
        "apm-card-small-4s.png",
        "apm-card-small-As.png",
        "apm-card-small-Jd.png",
        "apm-card-small-Kc.png",
        "apm-card-small-Kh.png",
        "apm-card-small-Qd.png",
        "apm-card-small-Ts.png",
    ]

    assert sorted([f.name for f in all_media_files]) == sorted(expected_media_files)

    for f in expected_media_files:
        compare_or_update_golden_with_path(
            pytestconfig,
            golden_dir / f,
            Path(collection.media.dir()) / f,
        )
