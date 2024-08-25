from typing import Any

import pytest

from anki_poker_master.model import ValidationError


def test_phh_parser_basic():
    from anki_poker_master.parser.phh import parse_phh
    from anki_poker_master.model.hand import Street

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
    assert hand.hero_cards == ['Th', '8c']
    assert len(hand.streets) == 1
    expected_preflop = Street(
        "Preflop",
        [],
        [6],
        [True, True, True],
        [108, 416, 450],
        2,
        [[], [], []]
    )
    assert hand.streets[0] == expected_preflop


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


def test_phh_parser_multiple_hole_cards_can_be_known_with_apm_hero():
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
_apm_hero = 2
"""
    hand = parse_phh(content)
    assert [p.is_hero for p in hand.players] == [False, True, False]


@pytest.mark.parametrize(
    'apm_hero',
    [-10, -1, 0, 4, 7]
)
def test_phh_parse_invalid_apm_hero_1(apm_hero: Any):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_hero = {apm_hero}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "must be between 1 and 3" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_hero',
    ['true', '"asdf"', '[]']
)
def test_phh_parse_invalid_apm_hero_2(apm_hero: Any):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_hero = {apm_hero}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'int'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_source',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_source(apm_source):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_source = {apm_source}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_notes',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_notes(apm_notes):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_notes = {apm_notes}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_context',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_context(apm_context):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_context = {apm_context}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_answers',
    ['true', '10']
)
def test_phh_parse_invalid_apm_answers_1(apm_answers):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_answers = {apm_answers}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'list'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_answers',
    ['[2]', '[true, 3]']
)
def test_phh_parse_invalid_apm_answers_2(apm_answers):
    from anki_poker_master.parser.phh import parse_phh
    content = f"""variant = "NT"
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
_apm_answers = {apm_answers}
"""
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


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


@pytest.mark.parametrize("variant", ["FT", "NS", "PO"])
def test_phh_parser_invalid_poker_variant(variant):
    from anki_poker_master.parser.phh import parse_phh

    content = f"""variant = "{variant}"
    antes = [0, 0, 0]
    blinds_or_straddles = [2, 4, 0]
    min_bet = 2
    small_bet = 2
    big_bet = 4
    starting_stacks = [110, 420, 450]
    actions = [
      # Pre-flop
      "d dh p1 ????",
      "d dh p2 Th8c",
      "d dh p3 ????",
    ]
    """
    with pytest.raises(ValidationError) as excinfo:
        parse_phh(content)
    assert f"the variant '{variant}' is not supported" in excinfo.value.humanize_error()


def test_phh_parser_with_preflop():
    from anki_poker_master.parser.phh import parse_phh
    from anki_poker_master.model.hand import Street

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
  "p3 cbr 12",
  "p1 f",
  "p2 cc",
]
"""
    hand = parse_phh(content)
    assert hand is not None
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]
    assert hand.hero_cards == ['Th', '8c']
    assert len(hand.streets) == 1
    expected_preflop = Street(
        "Preflop",
        [],
        [6],
        [True, True, True],
        [108, 416, 450],
        2,
        [["F"], ["C"], ["B 12"]]
    )

    assert hand.streets[0] == expected_preflop


def test_phh_parser_with_flop():
    from anki_poker_master.parser.phh import parse_phh
    from anki_poker_master.model.hand import Street

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
  "p3 cbr 12",
  "p1 f",
  "p2 cc",
  "d db AhTs8h",
]
"""
    hand = parse_phh(content)
    assert hand is not None
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]
    assert hand.hero_cards == ['Th', '8c']
    assert len(hand.streets) == 2
    expected_flop = Street(
        "Flop",
        ['Ah', 'Ts', '8h'],
        [26],
        [False, True, True],
        [108, 408, 438],
        0,
        [[], [], []]
    )

    assert hand.streets[1] == expected_flop
