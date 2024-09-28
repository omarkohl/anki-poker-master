"""
Test the presentation (e.g. HTML or Anki output) of hand histories.
"""
import re

import pytest

from anki_poker_master.model.hand import Player

from tests.utils import compare_or_update_golden


@pytest.mark.parametrize(
    "street_index, question_index",
    [
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (3, 0),
    ],
)
def test_get_question_success(pytestconfig, golden_dir, street_index, question_index):
    """
    Verify that the HTML output generated is correct for different questions (identified by the
    street and question index). Some extras such as CSS are added to make it more comfortable
    for humans to visually evaluate the output.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.html.phh import get_question

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
  "p3 cbr 20",
  "p2 cbr 40",
  "p3 cbr 80",
  "p2 cbr 160",
  "p3 cbr 320",
  "p2 cc",
  "d db Tc",
  "p2 cbr 68",
  "p3 f",
]
players = ["Naima", "Chao", "Ben"]

_apm_context = "Online game. Fairly tight. The blinds have only played a few hands each."
"""
    hand = parse(content)
    content = get_question(hand, street_index, question_index)

    # in order to preview the HTML files conveniently we prefix resources
    resources_prefix = "../../../../../anki_poker_master/resources/"

    content = f"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{resources_prefix}default.css">
</head>
<body>
""" + content + "</body>\n</html>\n"

    # prefix all html img src with the above prefix
    content = re.sub(r'<img src="(.*)"', f'<img src="{resources_prefix}images/\\1"', content)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / f"question_{street_index}_{question_index}.html",
        content,
    )


def test_html_output_for_large_numbers(pytestconfig, golden_dir):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.html.phh import get_question

    content = """# The first televised million dollar pot between Tom Dwan and Phil Ivey.
# Link: https://youtu.be/GnxFohpljqM

variant = "NT"
ante_trimming_status = true
antes = [500, 500, 500]
blinds_or_straddles = [1000, 2000, 0]
min_bet = 2000
starting_stacks = [1125600, 2000000, 553500]
actions = [
  # Pre-flop

  "d dh p1 Ac2d",  # Ivey
  "d dh p2 ????",  # Antonius
  "d dh p3 7h6h",  # Dwan

  "p3 cbr 7000",  # Dwan
  "p1 cbr 23000",  # Ivey
  "p2 f",  # Antonius
  "p3 cc",  # Dwan

  # Flop

  "d db Jc3d5c",

  "p1 cbr 35000",  # Ivey
  "p3 cc",  # Dwan

  # Turn

  "d db 4h",

  "p1 cbr 90000",  # Ivey
  "p3 cbr 232600",  # Dwan
  "p1 cbr 1067100",  # Ivey
  "p3 cc",  # Dwan

  # Showdown

  "p1 sm Ac2d",  # Ivey
  "p3 sm 7h6h",  # Dwan

  # River

  "d db Jh",
]
author = "Juho Kim"
event = "Full Tilt Million Dollar Cash Game S4E12"
year = 2009
players = ["Phil Ivey", "Patrik Antonius", "Tom Dwan"]
currency = "USD"

_apm_hero = 3

# File source: https://github.com/uoftcprg/phh-dataset/tree/b086f70/data/dwan-ivey-2009.phh
# Changes:
#  * Add _apm_hero
"""
    hand = parse(content)
    content = get_question(hand, 2, 1)

    # in order to preview the HTML files conveniently we prefix resources
    resources_prefix = "../../../../../anki_poker_master/resources/"

    content = f"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{resources_prefix}default.css">
</head>
<body>
""" + content + "</body>\n</html>\n"

    # prefix all html img src with the above prefix
    content = re.sub(r'<img src="(.*)"', f'<img src="{resources_prefix}images/\\1"', content)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / f"question.html",
        content,
    )


@pytest.mark.parametrize(
    "players, street_index_for_question, question_index, expected_err",
    [
        (
                [
                    Player("p1", False, True),
                    Player("p2", False, True),
                    Player("p3", True, False),
                ],
                0,
                0,
                "there are multiple heroes, namely p1, p2",

        ),
        (
                [
                    Player("p1", False, False),
                    Player("p2", False, False),
                    Player("p3", True, False),
                ],
                0,
                0,
                "there is no hero",
        ),
        (
                [
                    Player("p1", False, True),
                    Player("p2", True, False),
                    Player("p3", True, False),
                ],
                0,
                0,
                "there are multiple dealers, namely p2, p3",
        ),
        (
                [
                    Player("p1", False, True),
                    Player("p2", False, False),
                    Player("p3", False, False),
                ],
                0,
                0,
                "there is no dealer",
        ),
        (
                [
                    Player("p1", False, False),
                    Player("p2", False, False),
                    Player("p3", True, True),
                ],
                1,
                0,
                "there is no street with index 1",
        ),
        (
                [
                    Player("p1", False, False),
                    Player("p2", False, False),
                    Player("p3", True, True),
                ],
                0,
                1,
                "there is no question with index 1 in street Preflop",
        ),
    ],
)
def test_validate_players(players, street_index_for_question, question_index, expected_err):
    from anki_poker_master.model.hand import Hand, Street, Question
    from anki_poker_master.model import ValidationError
    from anki_poker_master.presenter.html.phh import get_question

    hand = Hand()
    hand.players = players
    hand.streets.append(
        Street(
            "Preflop",
            [],
            [1, 2, 0],
            [True, True, True],
            [199, 198, 200],
            2,
            [["B 50"], ["F"], ["F"]],
            [Question("What do you do?", "Bet high.", (0, 0))],
        )
    )

    with pytest.raises(ValidationError) as excinfo:
        get_question(hand, street_index_for_question, question_index)

    assert expected_err in excinfo.value.humanize_error()
