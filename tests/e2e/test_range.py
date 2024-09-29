"""
Test the 'range' subcommand.
"""
from pathlib import Path
from typing import List, Tuple
import anki
import anki.importing.apkg
from anki.collection import ImportAnkiPackageOptions, ImportAnkiPackageRequest

from tests.utils import compare_or_update_golden, compare_or_update_golden_with_path


def test_simple_scenario(pytestconfig, golden_dir, tmp_path):
    from anki_poker_master.cli import main_with_args

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
            "range",
            "-s",
            str(scenarios_file),
            "-o",
            str(pkg_path),
            "--tag",
            "poker",
            "-t",
            "e2e-test",
        ]
    )

    collection = anki.collection.Collection(str(tmp_path / "collection.anki2"))

    collection.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(pkg_path),
            options=ImportAnkiPackageOptions(
                with_scheduling=True,
                with_deck_configs=True
            ),
        )
    )

    assert set(collection.tags.all()) == {'poker', 'e2e-test'}
    assert len(collection.decks.all_names_and_ids()) == 4

    assert collection.decks.id_for_name("AnkiPokerMaster::Standard")
    assert collection.decks.id_for_name("AnkiPokerMaster::Detailed")

    assert collection.decks.card_count(
        collection.decks.id_for_name("AnkiPokerMaster::Standard"),
        False,
    ) == 32

    assert collection.decks.card_count(
        collection.decks.id_for_name("AnkiPokerMaster::Detailed"),
        False,
    ) == 169

    all_card_ids = collection.find_cards('')

    assert len(all_card_ids) == 201

    all_qa: List[Tuple[str, str]] = []
    for card in [collection.get_card(cid) for cid in all_card_ids]:
        all_qa.append((card.question(), card.answer()))

    # assert that there are no duplicate questions, just in case, otherwise
    # the golden file comparison below will no longer be deterministic
    assert len(set(qa[0] for qa in all_qa)) == 201

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
        'apm-card-2c.png',
        'apm-card-2h.png',
        'apm-card-3c.png',
        'apm-card-3h.png',
        'apm-card-4c.png',
        'apm-card-4h.png',
        'apm-card-5c.png',
        'apm-card-5h.png',
        'apm-card-6c.png',
        'apm-card-6h.png',
        'apm-card-7c.png',
        'apm-card-7h.png',
        'apm-card-8c.png',
        'apm-card-8h.png',
        'apm-card-9c.png',
        'apm-card-9h.png',
        'apm-card-Ac.png',
        'apm-card-Ah.png',
        'apm-card-Jc.png',
        'apm-card-Jh.png',
        'apm-card-Kc.png',
        'apm-card-Kh.png',
        'apm-card-Qc.png',
        'apm-card-Qh.png',
        'apm-card-Tc.png',
        'apm-card-Th.png',
        'apm-card-Xc.png',
        'apm-card-Xh.png'
    ]

    assert sorted([f.name for f in all_media_files]) == sorted(expected_media_files)

    for f in expected_media_files:
        compare_or_update_golden_with_path(
            pytestconfig,
            golden_dir / f,
            Path(collection.media.dir()) / f,
        )
