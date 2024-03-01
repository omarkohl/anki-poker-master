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
    assert len(decks[0].notes) == 26
    for note in decks[0].notes:
        assert note.model.name in ("APM Preflop", "APM Basic")

    assert decks[1].name == "AnkiPokerMaster::Detailed"
    assert len(decks[1].notes) == 169
    assert decks[1].notes[0].model.name == "APM Basic"

    assert isinstance(media_files, set)
    assert len(media_files) == 28

    deck_path = os.path.join(tmp_path, "AnkiPokerMaster.apkg")
    write_deck_to_file(decks[0], media_files, deck_path)
    assert os.path.exists(deck_path)
    assert os.path.getsize(deck_path) > 0


def test_row_question_cards():
    """
    Row questions are the ones that ask "What should you do with KXs?" and
    similar.
    """
    from anki_poker_master.anki import create_decks
    from anki_poker_master import PreflopScenario

    scenarios = [
        {
            "game": "NLHE",
            "position": "UTG",
            "scenario": "vs. 3bet",
            "ranges": {
                "Raise": Range("JJ+, AJ+, KJ+, QJ"),  # 4x4 top left
                "Call": Range("ATs-, KTs-, QTs-, ATo-A5o"),
            },
        }
    ]
    tags = ["test"]
    decks, media_files = create_decks(
        [PreflopScenario(**scenarios[0])],
        tags=tags,
    )

    deck = None
    for d in decks:
        if d.name == "AnkiPokerMaster::Standard":
            deck = d
            break
    assert deck is not None
    assert len(deck.notes) == 26
    expected_qa_pairs = [
        (
            "How should you play pairs?",
            "<b>Fold:</b> TT-<br><b>Raise:</b> JJ+<br>",
        ),
        (
            "How should you play AXs?",
            "<b>Call:</b> ATs-<br><b>Raise:</b> AJs+<br>",
        ),
        (
            "How should you play KXs (where K is higher)?",
            "<b>Call:</b> KTs-<br><b>Raise:</b> KJs+<br>",
        ),
        (
            "How should you play QXs (where Q is higher)?",
            "<b>Call:</b> QTs-<br><b>Raise:</b> QJs<br>",
        ),
        (
            "How should you play JXs (where J is higher)?",
            "<b>Fold:</b> J2s+<br>",
        ),
        (
            "How should you play TXs (where T is higher)?",
            "<b>Fold:</b> T2s+<br>",
        ),
        (
            "How should you play 9Xs (where 9 is higher)?",
            "<b>Fold:</b> 92s+<br>",
        ),
        (
            "How should you play 8Xs (where 8 is higher)?",
            "<b>Fold:</b> 82s+<br>",
        ),
        (
            "How should you play 7Xs (where 7 is higher)?",
            "<b>Fold:</b> 72s+<br>",
        ),
        (
            "How should you play 6Xs (where 6 is higher)?",
            "<b>Fold:</b> 62s+<br>",
        ),
        (
            "How should you play 5Xs (where 5 is higher)?",
            "<b>Fold:</b> 52s+<br>",
        ),
        (
            "How should you play 4Xs (where 4 is higher)?",
            "<b>Fold:</b> 42s+<br>",
        ),
        (
            "How should you play 3Xs (where 3 is higher)?",
            "<b>Fold:</b> 32s<br>",
        ),
        (
            "How should you play AXo?",
            "<b>Call:</b> ATo-A5o<br><b>Fold:</b> A4o-<br><b>Raise:</b> AJo+<br>",
        ),
        (
            "How should you play KXo (where K is higher)?",
            "<b>Fold:</b> KTo-<br><b>Raise:</b> KJo+<br>",
        ),
        (
            "How should you play QXo (where Q is higher)?",
            "<b>Fold:</b> QTo-<br><b>Raise:</b> QJo<br>",
        ),
        (
            "How should you play JXo (where J is higher)?",
            "<b>Fold:</b> J2o+<br>",
        ),
        (
            "How should you play TXo (where T is higher)?",
            "<b>Fold:</b> T2o+<br>",
        ),
        (
            "How should you play 9Xo (where 9 is higher)?",
            "<b>Fold:</b> 92o+<br>",
        ),
        (
            "How should you play 8Xo (where 8 is higher)?",
            "<b>Fold:</b> 82o+<br>",
        ),
        (
            "How should you play 7Xo (where 7 is higher)?",
            "<b>Fold:</b> 72o+<br>",
        ),
        (
            "How should you play 6Xo (where 6 is higher)?",
            "<b>Fold:</b> 62o+<br>",
        ),
        (
            "How should you play 5Xo (where 5 is higher)?",
            "<b>Fold:</b> 52o+<br>",
        ),
        (
            "How should you play 4Xo (where 4 is higher)?",
            "<b>Fold:</b> 42o+<br>",
        ),
        (
            "How should you play 3Xo (where 3 is higher)?",
            "<b>Fold:</b> 32o<br>",
        ),
    ]
    was_tested = {q: False for q, a in expected_qa_pairs}

    for note in deck.notes:
        if note.model.name == "APM Preflop":
            continue
        assert note.model.name == "APM Basic"
        for expected_q, expected_a in expected_qa_pairs:
            if expected_q in note.fields[0]:
                assert expected_a in note.fields[1]
                was_tested[expected_q] = True

    for q, tested in was_tested.items():
        assert tested, f"Question '{q}' was not tested"
