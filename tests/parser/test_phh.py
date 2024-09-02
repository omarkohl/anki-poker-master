import os
import pathlib
from numbers import Number
from typing import Any, List

import pytest


def test_parser_basic():
    from anki_poker_master.parser.phh import parse
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

_apm_source = "https://example.com"
_apm_notes = "The point of this hand is to demonstrate correct play against TAGs."
_apm_context = \"""Online game. You have been playing for 2 hours.
The SB is very tight.
\"""
"""
    hand = parse(content)
    assert hand is not None
    assert hand.title == "NLHE 2/4"
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]
    assert hand.hero_cards == ['Th', '8c']
    assert hand.source == "https://example.com"
    assert hand.notes == "The point of this hand is to demonstrate correct play against TAGs."
    assert hand.context == "Online game. You have been playing for 2 hours.\nThe SB is very tight.\n"
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


def test_parser_player_names():
    """
    If players are specified, their names are used.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Player

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

players = ["Tom", "Naima", "Carlos"]
"""
    hand = parse(content)
    assert hand.players == [
        Player("Tom", False, False),
        Player("Naima", False, True),
        Player("Carlos", True, False),
    ]


def test_parser_hero_hole_cards_must_be_known():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "The hole cards of the hero must be known." in excinfo.value.humanize_error()


def test_parser_multiple_players_could_be_hero_error():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "It is unclear who the hero is." in excinfo.value.humanize_error()


def test_parser_multiple_hole_cards_can_be_known_with_apm_hero():
    from anki_poker_master.parser.phh import parse
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
    hand = parse(content)
    assert [p.is_hero for p in hand.players] == [False, True, False]


@pytest.mark.parametrize(
    'apm_hero',
    [-10, -1, 0, 4, 7]
)
def test_phh_parse_invalid_apm_hero_1(apm_hero: Any):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "must be between 1 and 3" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_hero',
    ['true', '"asdf"', '[]']
)
def test_phh_parse_invalid_apm_hero_2(apm_hero: Any):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'int'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_source',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_source(apm_source):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_notes',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_notes(apm_notes):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_context',
    ['true', '10', '[]']
)
def test_phh_parse_invalid_apm_context(apm_context):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_answers',
    ['true', '10']
)
def test_phh_parse_invalid_apm_answers_1(apm_answers):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'list'" in excinfo.value.humanize_error()


@pytest.mark.parametrize(
    'apm_answers',
    ['[2]', '[true, 3]']
)
def test_phh_parse_invalid_apm_answers_2(apm_answers):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError
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
        parse(content)
    assert "should be instance of 'str'" in excinfo.value.humanize_error()


def test_parser_empty_apm_source_notes_context_are_ignored():
    """
    _apm_source and _apm_context are set to an empty string and _apm_notes is missing. In all
    cases the result is an empty string in the final hand object.
    """
    from anki_poker_master.parser.phh import parse

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

_apm_source = ""
_apm_context = ""
"""
    hand = parse(content)
    assert hand.source == ""
    assert hand.notes == ""
    assert hand.context == ""


def test_parser_emtpy_file():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError

    with pytest.raises(ValidationError) as excinfo:
        parse("")
    assert "Invalid PHH (empty)" in excinfo.value.humanize_error()


def test_parser_incomplete_file():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError

    content = """variant = "NT"
antes = [0, 0, 0, 0, 0, 0, 0, 0, 0]
"""
    with pytest.raises(ValidationError) as excinfo:
        parse(content)
    assert "Error parsing PHH with content:" in excinfo.value.humanize_error()


@pytest.mark.parametrize("variant", ["NS", "PO"])
def test_parser_invalid_poker_variant(variant):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError

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
        parse(content)
    assert f"the variant '{variant}' is not supported" in excinfo.value.humanize_error()


def test_parser_with_preflop():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Street, Question

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
    hand = parse(content)
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
        [["B 12"], ["F"], ["C"]],
        [Question("What do you do?", "C", (2, 0))],
    )

    assert hand.streets[0] == expected_preflop


def test_parser_with_flop():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Street, Question

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
  "p2 cc",
  "p3 cbr 20",
  "p2 cc",
]
"""
    hand = parse(content)
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
        [[], ["X", "C"], ["B 20"]],
        [
            Question("What do you do?", "X", (1, 0)),
            Question("What do you do?", "C", (1, 1)),
        ],
    )

    assert hand.streets[1] == expected_flop


def test_parser_with_turn():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Street, Question

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
  "p2 cc",
  "p3 cbr 20",
  "p2 cc",
  "d db 4s",
  "p2 cc",
  "p3 cc",
]
"""
    hand = parse(content)
    assert hand is not None
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]
    assert hand.hero_cards == ['Th', '8c']
    assert len(hand.streets) == 3
    expected_turn = Street(
        "Turn",
        ['Ah', 'Ts', '8h', '4s'],
        [66],
        [False, True, True],
        [108, 388, 418],
        0,
        [[], ["X"], ["X"]],
        [
            Question("What do you do?", "X", (1, 0)),
        ],
    )

    assert hand.streets[2] == expected_turn


def test_parser_with_river():
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Street, Question

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
    hand = parse(content)
    assert hand is not None
    assert len(hand.players) == 3
    assert hand.players[1].name == "p2"
    assert [p.is_dealer for p in hand.players] == [False, False, True]
    assert [p.is_hero for p in hand.players] == [False, True, False]
    assert hand.hero_cards == ['Th', '8c']
    assert len(hand.streets) == 4
    expected_river = Street(
        "River",
        ['Ah', 'Ts', '8h', '4s', 'Tc'],
        [66],
        [False, True, True],
        [108, 388, 418],
        0,
        [[], ["B 388"], ["F"]],
        [
            Question("What do you do?", "B 388", (1, 0)),
        ],
    )

    assert hand.streets[3] == expected_river


def test_parser_questions():
    """
    Test that it's possible to include questions (study spots) and answers in the the .phh file.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Question

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
      "p2 cc # apm study",
      "d db AhTs8h",
      "p2 cc",
      "p3 cbr 20",
      "p2 cc # APM study: Check, but 3bet to 60 would be fine too.",
      "d db 4s",
      "p2 cc",
      "p3 cc",
      "d db Tc",
      "p2 cbr 388 # APM Study",
      "p3 f",
    ]

    _apm_answers = [
        "",
        "Check",
        "Going all in is best."
    ]
    """
    hand = parse(content)
    assert hand.streets[0].questions is not None
    assert len(hand.streets[0].questions) == 1
    assert len(hand.streets[1].questions) == 1
    assert len(hand.streets[2].questions) == 0
    assert len(hand.streets[3].questions) == 1

    assert hand.streets[0].questions[0] == Question(
        "What do you do?",
        "C",
        (2, 0),
    )
    # Note that the inline answer takes precedence over the one in _apm_answers
    assert hand.streets[1].questions[0] == Question(
        "What do you do?",
        "Check, but 3bet to 60 would be fine too.",
        (1, 1),
    )
    assert hand.streets[3].questions[0] == Question(
        "What do you do?",
        "Going all in is best.",
        (1, 0),
    )


def test_parser_questions_if_apm_answers_are_specified_length_must_match():
    """
    Verify that the length of the _apm_answers user-defined field must match the number of
    questions (study spots) in the hand.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model import ValidationError

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
      "p2 cc # apm study",
      "d db AhTs8h",
      "p2 cc",
      "p3 cbr 20",
      "p2 cc # APM study: Check, but 3bet to 60 would be fine too.",
      "d db 4s",
      "p2 cc",
      "p3 cc",
      "d db Tc",
      "p2 cbr 388 # APM Study",
      "p3 f",
    ]

    _apm_answers = [
        "",
        "Check",
        "Going all in is best.",
        "",
    ]
    """
    with pytest.raises(ValidationError) as excinfo:
        parse(content)

    assert "_apm_answers contains 4 answers but 3 questions are asked" in str(excinfo.value)


def test_parser_questions_default_all_hero_actions():
    """
    Test that if no explicit questions (study spots) are specified via commentaries then every
    action by the hero is a study spot by default.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.model.hand import Question

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

    _apm_answers = [
        "80% Call, 20% Raise.",
        "Check and only very rarely bet as a bluff.",
        "Call.",
        "",
        "Go all in.",
    ]
    """
    hand = parse(content)
    assert hand.streets[0].questions is not None
    assert len(hand.streets[0].questions) == 1
    assert len(hand.streets[1].questions) == 2
    assert len(hand.streets[2].questions) == 1
    assert len(hand.streets[3].questions) == 1

    assert hand.streets[0].questions[0] == Question(
        "What do you do?",
        "80% Call, 20% Raise.",
        (2, 0),
    )
    assert hand.streets[1].questions[0] == Question(
        "What do you do?",
        "Check and only very rarely bet as a bluff.",
        (1, 0),
    )
    assert hand.streets[1].questions[1] == Question(
        "What do you do?",
        "Call.",
        (1, 1),
    )
    assert hand.streets[2].questions[0] == Question(
        "What do you do?",
        "X",
        (1, 0),
    )
    assert hand.streets[3].questions[0] == Question(
        "What do you do?",
        "Go all in.",
        (1, 0),
    )


def test_parser_with_same_antes_for_all():
    from anki_poker_master.parser.phh import parse

    content = """variant = "NT"
    antes = [1, 1, 1]
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
    hand = parse(content)
    assert hand.title == "NLHE 2/4 (ante 1)"


def test_parser_with_different_antes():
    from anki_poker_master.parser.phh import parse

    content = """variant = "NT"
    antes = [0, 3, 0]
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
    hand = parse(content)
    assert hand.title == "NLHE 2/4 (ante 1)"


@pytest.mark.parametrize(
    "file_name, expected_initial_stacks_last_street",
    [
        (
                "00-18-39.phh",
                [
                    7750000,
                    4125000,
                    8525000,
                    4550000,
                    4050000,
                ]
        ),
        (
                "02-53-09.phh",
                [
                    2125000,
                    2200000,
                    3125000,
                    2375000,
                    19425000,
                ]
        ),
        (
                "00-15-36.phh",
                [
                    4050000,
                    8250000,
                    4550000,
                    8525000,
                    3375000,
                ]
        ),
        (
                "dwan-ivey-2009.phh",
                [
                    # Note that by this point the hand is over and p3 (Tom Dwan) has won.
                    572100,
                    1997500,
                    1109500,
                ]
        ),
        (
                # This is a FT (limit hold'em) hand, to demonstrate that it's possible
                "01-51-27.phh",
                [
                    14325000,
                    7250000,
                    2850000,
                    2500000,
                    475000,
                ]
        ),
    ]
)
def test_parser_example_files_success(
        testdata_dir: pathlib.Path,
        file_name: str,
        expected_initial_stacks_last_street: List[Number],
) -> None:
    """
    Parse same example .phh files and perform some minimal verification.
    """
    from anki_poker_master.parser.phh import parse

    content = (testdata_dir / file_name).read_text('utf8')
    hand = parse(content)
    assert hand.streets
    assert hand.streets[-1].initial_stacks == expected_initial_stacks_last_street
