from poker.hand import Range
import genanki
import os


def test_deck_is_created(tmp_path):
    from anki_poker_master.presenter.anki.preflop_scenario import write_deck_to_file
    from anki_poker_master.presenter.anki.preflop_scenario import create_decks
    from anki_poker_master.model import PreflopScenario

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
    from anki_poker_master.presenter.anki.preflop_scenario import create_decks
    from anki_poker_master.model import PreflopScenario

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
            "<b>Fold:</b> TT-<br><b>Raise:</b> JJ+",
        ),
        (
            "How should you play AXs?",
            "<b>Call:</b> ATs-<br><b>Raise:</b> AJs, AQs, AKs",
        ),
        (
            "How should you play KXs (where K is higher)?",
            "<b>Call:</b> KTs-<br><b>Raise:</b> KJs, KQs",
        ),
        (
            "How should you play QXs (where Q is higher)?",
            "<b>Call:</b> QTs-<br><b>Raise:</b> QJs",
        ),
        (
            "How should you play JXs (where J is higher)?",
            "<b>Fold:</b> All (J2s+)",
        ),
        (
            "How should you play TXs (where T is higher)?",
            "<b>Fold:</b> All (T2s+)",
        ),
        (
            "How should you play 9Xs (where 9 is higher)?",
            "<b>Fold:</b> All (92s+)",
        ),
        (
            "How should you play 8Xs (where 8 is higher)?",
            "<b>Fold:</b> All (82s+)",
        ),
        (
            "How should you play 7Xs (where 7 is higher)?",
            "<b>Fold:</b> All (72s+)",
        ),
        (
            "How should you play 6Xs (where 6 is higher)?",
            "<b>Fold:</b> All (62s+)",
        ),
        (
            "How should you play 5Xs (where 5 is higher)?",
            "<b>Fold:</b> All (52s, 53s, 54s)",
        ),
        (
            "How should you play 4Xs (where 4 is higher)?",
            "<b>Fold:</b> All (42s, 43s)",
        ),
        (
            "How should you play 3Xs (where 3 is higher)?",
            "<b>Fold:</b> All (32s)",
        ),
        (
            "How should you play AXo?",
            "<b>Call:</b> ATo-A5o<br><b>Fold:</b> A2o, A3o, A4o<br><b>Raise:</b> AJo, AQo, AKo",
        ),
        (
            "How should you play KXo (where K is higher)?",
            "<b>Fold:</b> KTo-<br><b>Raise:</b> KJo, KQo",
        ),
        (
            "How should you play QXo (where Q is higher)?",
            "<b>Fold:</b> QTo-<br><b>Raise:</b> QJo",
        ),
        (
            "How should you play JXo (where J is higher)?",
            "<b>Fold:</b> All (J2o+)",
        ),
        (
            "How should you play TXo (where T is higher)?",
            "<b>Fold:</b> All (T2o+)",
        ),
        (
            "How should you play 9Xo (where 9 is higher)?",
            "<b>Fold:</b> All (92o+)",
        ),
        (
            "How should you play 8Xo (where 8 is higher)?",
            "<b>Fold:</b> All (82o+)",
        ),
        (
            "How should you play 7Xo (where 7 is higher)?",
            "<b>Fold:</b> All (72o+)",
        ),
        (
            "How should you play 6Xo (where 6 is higher)?",
            "<b>Fold:</b> All (62o+)",
        ),
        (
            "How should you play 5Xo (where 5 is higher)?",
            "<b>Fold:</b> All (52o, 53o, 54o)",
        ),
        (
            "How should you play 4Xo (where 4 is higher)?",
            "<b>Fold:</b> All (42o, 43o)",
        ),
        (
            "How should you play 3Xo (where 3 is higher)?",
            "<b>Fold:</b> All (32o)",
        ),
    ]
    was_tested = {q: False for q, a in expected_qa_pairs}

    for note in deck.notes:
        if note.model.name == "APM Preflop":
            continue
        assert note.model.name == "APM Basic"
        a_question_was_found = False
        for expected_q, expected_a in expected_qa_pairs:
            if expected_q in note.fields[0]:
                a_question_was_found = True
                assert expected_a in note.fields[1]
                was_tested[expected_q] = True
        assert a_question_was_found, f"No question was found in:\n{note.fields[0]}"

    for q, tested in was_tested.items():
        assert tested, f"Question '{q}' was not tested"
