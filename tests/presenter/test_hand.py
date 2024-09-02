"""
Test the presentation (e.g. HTML or Anki output) of hand histories.
"""

from tests.utils import compare_or_update_golden


def test_hand_to_html_basic(pytestconfig, golden_dir):
    from anki_poker_master.parser.phh import parse
    from anki_poker_master.presenter.hand import to_html

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
    content = to_html(hand)

    compare_or_update_golden(
        pytestconfig,
        golden_dir / "index.html",
        content,
    )
