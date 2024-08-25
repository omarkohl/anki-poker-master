import pytest

from anki_poker_master.model import ValidationError


def test_phh_parser():
    from anki_poker_master.parser.phh import parse_phh

    content = """variant = "NT"
antes = [0, 0, 0, 0, 0, 0, 0, 0, 0]
blinds_or_straddles = [2, 4, 0, 0, 0, 0, 0, 0, 0]
min_bet = 2
starting_stacks = [110, 420, 450, 340, 280, 400, 570, 100, 990]
actions = [
  # Pre-flop
  "d dh p1 ????",
  "d dh p2 ????",
  "d dh p3 ????",
  "d dh p4 ????",
  "d dh p5 ????",
  "d dh p6 ????",
  "d dh p7 Th8c",
  "d dh p8 ????",
  "d dh p9 ????",
]
"""
    hand = parse_phh(content)
    assert hand is not None
    assert len(hand.players) == 9
    assert hand.players[1].name == "p2"
    assert hand.players[8].is_dealer



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
