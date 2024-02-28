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
                "Call": Range("98+, A8+, K8+, Q8+, J8+, T8+"),
                "Raise": Range("88+"),
            },
            "notes": "This is a test",
        }
    ]
    tags = ["test"]
    decks, media_files = create_decks(
        [PreflopScenario(**scenarios[0])],
        tags=tags,
    )
    # Just perform some basic sanity checks
    assert isinstance(decks, list)
    assert len(decks) == 2
    for deck in decks:
        assert isinstance(deck, genanki.Deck)
    assert decks[0].name == "AnkiPokerMaster::Standard"
    assert len(decks[0].notes) == 28
    for note in decks[0].notes:
        assert note.model.name in ("Poker Preflop Scenario", "Basic with source")

    assert decks[1].name == "AnkiPokerMaster::Detailed"
    assert len(decks[1].notes) == 169
    assert decks[1].notes[0].model.name == "Basic with source"

    assert isinstance(media_files, set)
    assert len(media_files) == 28

    deck_path = os.path.join(tmp_path, "AnkiPokerMaster.apkg")
    write_deck_to_file(decks[0], media_files, deck_path)
    assert os.path.exists(deck_path)
    assert os.path.getsize(deck_path) > 0
