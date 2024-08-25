import pytest

from anki_poker_master.model import ValidationError


def test_phh_parser_basic():
    from anki_poker_master.parser.phh import parse_phh

    content = """variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
  # Pre-flop
  "d dh p1 ????",
  "d dh p2 Th8c",
  "d dh p3 ????",
]
"""
    hand = parse_phh(content)
    assert hand is not None
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]


def test_phh_parser_hero_hole_cards_must_be_known():
    from anki_poker_master.parser.phh import parse_phh
    content = """variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
  # Pre-flop
  "d dh p1 ????",
  "d dh p2 ????",
  "d dh p3 ????",
]
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "The hole cards of the hero must be known." in excinfo.value.humanize_error()


def test_phh_parser_only_one_players_hole_cards_must_be_known():
    from anki_poker_master.parser.phh import parse_phh
    content = """variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
  # Pre-flop
  "d dh p1 ????",
  "d dh p2 Th7s",
  "d dh p3 AsAc",
]
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "The hole cards of only one player must be known." in excinfo.value.humanize_error()


def test_phh_parser_emtpy_file():
    from anki_poker_master.parser.phh import parse_phh
    with pytest.raises(ValidationError) as excinfo:
        parse_phh("")
    assert "Invalid PHH (empty)" in excinfo.value.humanize_error()


def test_phh_parser_incomplete_file():
    from anki_poker_master.parser.phh import parse_phh
    content = """variant = "NT"
antes = [0, 0, 0, 0, 0, 0, 0, 0, 0]
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "Error parsing PHH with content:" in excinfo.value.humanize_error()
