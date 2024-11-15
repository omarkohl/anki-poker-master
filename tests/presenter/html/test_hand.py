"""
Test the presentation (e.g. HTML or Anki output) of hand histories.
"""

import re

import pytest

from anki_poker_master.model.hand import Player

from tests.utils import compare_or_update_golden

# in order to preview the HTML files conveniently we prefix resources
RESOURCES_PREFIX = "../../../../../../anki_poker_master/resources/"


def _create_html_content(content, dark_mode=False):
    """
    Helper function to create a full HTML document with the given content. It
    makes it easier to visually inspect the HTML output.
    """
    content = re.sub(
        r'<img src="(.*)"',
        f'<img src="{RESOURCES_PREFIX}images/\\1"',
        content,
    )
    header = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{RESOURCES_PREFIX}default.css">
</head>
"""
    if dark_mode:
        return (
            header
            + '<body style="background-color: #221e1e">\n'
            + '<div class="nightMode">\n'
            + content
            + "</div>\n"
            + "</body>\n"
            + "</html>\n"
        )
    else:
        return header + "<body>\n" + content + "</body>\n" + "</html>\n"


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

    compare_or_update_golden(
        pytestconfig,
        golden_dir / f"question_{street_index}_{question_index}.html",
        _create_html_content(content),
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

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "question.html",
        _create_html_content(content),
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
def test_validate_players(
    players, street_index_for_question, question_index, expected_err
):
    from anki_poker_master.model.hand import (
        Hand,
        Street,
        Question,
        BetAction,
        FoldAction,
    )
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
            [[BetAction(50)], [FoldAction()], [FoldAction()]],
            [Question("What do you do?", "Bet high.", (0, 0))],
        )
    )

    with pytest.raises(ValidationError) as excinfo:
        get_question(hand, street_index_for_question, question_index)

    assert expected_err in excinfo.value.humanize_error()


def test_mobile_dark_mode(testdata_dir, golden_dir, pytestconfig):
    """
    Generate HTML output for a hand history and compare it to the golden file.
    This test is for "mobile" and "dark mode" only in the sense that the
    generated HTML has a dark background and can be viewed in mobile view.
    The test exists mostly as a convenience for manual preview and testing of
    the HTML result.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.html.phh import get_question

    file_content = (testdata_dir / "harrington-cash-10-13.phh").read_text()
    hand = parse(file_content)

    content = get_question(hand, 3, 1)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "question_light.html",
        _create_html_content(content, False),
    )

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "question_dark.html",
        _create_html_content(content, True),
    )


def test_pot_rounding(testdata_dir, golden_dir, pytestconfig):
    """
    Generate HTML output for a hand history and compare it to the golden file. There was a bug that
    caused the pot not to be rounded in the HTML output so this test ensures there is no regression.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.html.phh import get_question

    file_content = (testdata_dir / "harrington-cash-10-11.phh").read_text()
    hand = parse(file_content)

    content = get_question(hand, 2, 0)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "question.html",
        _create_html_content(content),
    )


def test_long_history(testdata_dir, golden_dir, pytestconfig):
    """
    Generate HTML output for a long hand history and compare it to the golden
    file. The main reason for this test is to have a long hand history to
    visually examine the HTML output in order to maybe tweak it.
    """
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.html.phh import get_question

    file_content = (testdata_dir / "long_history.phh").read_text()
    hand = parse(file_content)

    content = get_question(hand, 2, 0)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "question.html",
        _create_html_content(content),
    )
