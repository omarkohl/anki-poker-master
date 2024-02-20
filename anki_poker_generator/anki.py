import random
import genanki
from anki_poker_generator import PreflopScenario
from anki_poker_generator.const import BLANK_TABLE
from typing import List

_HEADER_FMT = "{{CSS}}<b>Game: </b>{{Game}}<br><b>Position: </b>{{Position}}<br><b>Scenario: </b>{{Scenario}}<br>"
_FOOTER_FMT = "<br>{{Ranges}}<br><b>Notes: </b>{{Notes}}<br><b>Source: </b>{{Source}}<br>"

_PREFLOP_MODEL = genanki.Model(
    1995683082, # Random number that should not change in the future
    'Poker Preflop',
    fields=[
        {'name': 'Game'},
        {'name': 'Position'},
        {'name': 'Scenario'},
        {'name': 'Ranges'},
        {'name': 'Notes'},
        {'name': 'Source'},
        {'name': 'Full HTML'},
        {'name': 'Top Left Quadrant Blank HTML'},
        {'name': 'Top Right Quadrant Blank HTML'},
        {'name': 'Bottom Left Quadrant Blank HTML'},
        {'name': 'Bottom Right Quadrant Blank HTML'},
        {'name': 'CSS'},
        {'name': 'Legend'},
    ],
    templates=[
        {
            'name': 'TL Quadrant',
            'qfmt': _HEADER_FMT + '{{Top Left Quadrant Blank HTML}}' + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        },
        {
            'name': 'TR Quadrant',
            'qfmt': _HEADER_FMT + '{{Top Right Quadrant Blank HTML}}' + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        },
        {
            'name': 'BL Quadrant',
            'qfmt': _HEADER_FMT + '{{Bottom Left Quadrant Blank HTML}}' + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        },
        {
            'name': 'BR Quadrant',
            'qfmt': _HEADER_FMT + '{{Bottom Right Quadrant Blank HTML}}' + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        },
        {
            'name': 'Full',
            'qfmt': _HEADER_FMT + BLANK_TABLE + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        },
        {
            'name': 'Guess Position',
            'qfmt': "{{CSS}}<b>Game: </b>{{Game}}<br><b>Position: </b>?<br><b>Scenario: </b>{{Scenario}}<br>" +
                '{{Full HTML}}' + '<br>{{Legend}}',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT,
        }
    ],
)


def create_deck(scenarios: List[PreflopScenario]) -> List[genanki.Deck]:
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, "Poker Preflop")
    for scenario in scenarios:
        ranges_txt = ""
        for action in sorted(scenario.ranges):
            percentage = scenario.ranges[action].percent
            ranges_txt += f"<b>{action}</b> ({percentage}%): {scenario.ranges[action]}<br>"
        deck.add_note(genanki.Note(
            model=_PREFLOP_MODEL,
            fields=[
                scenario.game,
                scenario.position,
                scenario.scenario,
                ranges_txt,
                scenario.notes if scenario.notes else "",
                scenario.source if scenario.source else "",
                scenario.html_full(),
                scenario.html_top_left_quadrant_blank(),
                scenario.html_top_right_quadrant_blank(),
                scenario.html_bottom_left_quadrant_blank(),
                scenario.html_bottom_right_quadrant_blank(),
                scenario.css(),
                scenario.html_legend(),
            ],
        ))
    return deck

def write_deck_to_file(deck: genanki.Deck, filename: str):
    genanki.Package(deck).write_to_file(filename)
