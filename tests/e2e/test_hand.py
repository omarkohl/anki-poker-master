"""
Test the 'hand' subcommand.
"""

from pathlib import Path
from typing import List, Tuple
import anki
import anki.importing.apkg
from anki.collection import ImportAnkiPackageOptions, ImportAnkiPackageRequest

from tests.utils import compare_or_update_golden, compare_or_update_golden_with_path


def test_pure_phh_file(pytestconfig, golden_dir, tmp_path):
    """
    Verify that when calling anki-poker-master with a "normal" phh file an
    Anki deck is generated and contains the notes, cards, tags etc. we expect.
    """
    from anki_poker_master.cli import main_with_args

    phh_f = tmp_path / "hand.phh"
    phh_f.write_text(
        """variant = "NT"
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
""",
        encoding="utf-8",
    )

    collection = anki.collection.Collection(str(tmp_path / "collection.anki2"))
    pkg_f = tmp_path / "package.apkg"

    main_with_args([
        "hand",
        "-t",
        "poker",
        "-o",
        str(pkg_f),
        str(phh_f),
    ])

    collection.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(pkg_f),
            options=ImportAnkiPackageOptions(
                with_scheduling=True,
                with_deck_configs=True
            ),
        )
    )

    assert collection.tags.all() == ['poker']
    assert len(collection.decks.all_names_and_ids()) == 3
    deck_id = collection.decks.id_for_name("AnkiPokerMaster::HandHistory")
    assert deck_id
    all_notes_ids = collection.find_notes('')
    assert len(all_notes_ids) == 5

    for note in [collection.get_note(nid) for nid in all_notes_ids]:
        assert len(note.fields) == 4

    all_card_ids = collection.find_cards('')

    assert len(all_card_ids) == 5

    all_qa: List[Tuple[str, str]] = []
    for card in [collection.get_card(cid) for cid in all_card_ids]:
        all_qa.append((card.question(), card.answer()))

    # assert that there are no duplicate questions, just in case, otherwise
    # the golden file comparison below will no longer be deterministic
    assert len(set(qa[0] for qa in all_qa)) == 5

    # sort them to ensure a deterministic order in the golden files
    all_qa = sorted(all_qa, key=lambda qa: qa[0])

    for i, (q, a) in enumerate(all_qa):
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"answer_{i:02}.html",
            a,
        )
        compare_or_update_golden(
            pytestconfig,
            golden_dir / f"question_{i:02}.html",
            q,
        )

    all_media_files = list(Path(collection.media.dir()).rglob("*"))

    expected_media_files = [
        'apm-card-small-4s.png',
        'apm-card-small-8c.png',
        'apm-card-small-8h.png',
        'apm-card-small-Ah.png',
        'apm-card-small-Tc.png',
        'apm-card-small-Th.png',
        'apm-card-small-Ts.png',
    ]

    assert sorted([f.name for f in all_media_files]) == sorted(expected_media_files)

    for f in expected_media_files:
        compare_or_update_golden_with_path(
            pytestconfig,
            golden_dir / f,
            Path(collection.media.dir()) / f,
        )
