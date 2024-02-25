from poker.hand import Range
import genanki
import os


def test_deck_is_created(tmp_path):
    from anki_poker_master.anki import create_decks, write_deck_to_file
    from anki_poker_master import PreflopScenario

    scenarios = [
        {
            "game": "NLHE",
            "position": "UTG",
            "scenario": "Top left",
            "ranges": {
                "Fold": Range("XX"),
                "Call": Range("98+, A8+, K8+, Q8+, J8+, T8+, 88+"),
                "Raise": Range("88+"),
            },
            "notes": "This is a test",
        }
    ]
    config = {
        "tags": ["test"],
    }
    decks = create_decks(
        [PreflopScenario(**scenarios[0])],
        tags=config.get("tags", None),
    )
    # Just perform some basic sanity checks
    assert isinstance(decks, list)
    assert len(decks) == 1
    assert isinstance(decks[0], genanki.Deck)
    assert decks[0].name == "AnkiPokerMaster"
    assert len(decks[0].notes) == 1
    assert len(decks[0].notes[0].fields) == 14
    assert len(decks[0].notes[0].tags) == 1
    assert decks[0].notes[0].model.name == "Poker Preflop Scenario"
    assert len(decks[0].notes[0].model.templates) == 7

    deck_path = os.path.join(tmp_path, "AnkiPokerMaster.apkg")
    write_deck_to_file(decks[0], deck_path)
    assert os.path.exists(deck_path)
    assert os.path.getsize(deck_path) > 0
