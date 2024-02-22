import random
import genanki
from anki_poker_generator import PreflopScenario
from anki_poker_generator.const import BLANK_TABLE, DEFAULT_CSS, DEFAULT_JS
from typing import List

_HEADER_FMT = "<style>{{CSS}}</style><b>Game: </b>{{Game}}<br><b>Scenario: </b>{{Scenario}}<br><b>Position: </b>{{Position}}<br>"
_FOOTER_FMT = "<br>{{Ranges}}<br><b>Notes: </b>{{Notes}}<br><b>Source: </b>{{Source}}<br>"

_PREFLOP_MODEL = genanki.Model(
    1995683082, # Random number that should not change in the future
    'Poker Preflop',
    fields=[
        # The first field is just to avoid the 'Duplicate' warning in Anki
        # that checks for the first field.
        {'name': 'Summary'},
        {'name': 'Game'},
        {'name': 'Scenario'},
        {'name': 'Position'},
        {'name': 'Ranges'},
        {'name': 'Notes'},
        {'name': 'Source'},
        {'name': 'Full HTML', 'collapsed': True},
        {'name': 'Top Left Quadrant Blank HTML', 'collapsed': True},
        {'name': 'Top Right Quadrant Blank HTML', 'collapsed': True},
        {'name': 'Bottom Left Quadrant Blank HTML', 'collapsed': True},
        {'name': 'Bottom Right Quadrant Blank HTML', 'collapsed': True},
        {'name': 'CSS', 'collapsed': True},
        {'name': 'Legend', 'collapsed': True},
    ],
    templates=[
        {
            'name': 'TL Quadrant',
            'qfmt': _HEADER_FMT + '{{Top Left Quadrant Blank HTML}}' + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        },
        {
            'name': 'TR Quadrant',
            'qfmt': _HEADER_FMT + '{{Top Right Quadrant Blank HTML}}' + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        },
        {
            'name': 'BL Quadrant',
            'qfmt': _HEADER_FMT + '{{Bottom Left Quadrant Blank HTML}}' + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        },
        {
            'name': 'BR Quadrant',
            'qfmt': _HEADER_FMT + '{{Bottom Right Quadrant Blank HTML}}' + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        },
        {
            'name': 'Full',
            'qfmt': _HEADER_FMT + BLANK_TABLE + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        },
        {
            'name': 'Guess Position',
            'qfmt': "<style>{{CSS}}</style><b>Game: </b>{{Game}}<br>" +
                "<b>Scenario: </b>{{Scenario}}<br><b>Position: </b>?<br>" +
                '{{Full HTML}}' + '<br>{{Legend}}' + '<script>' + DEFAULT_JS + '</script>',
            'afmt': _HEADER_FMT + '{{Full HTML}}' + '<br>{{Legend}}' + _FOOTER_FMT + '<script>' + DEFAULT_JS + '</script>' ,
        }
    ],
    css=DEFAULT_CSS,
)


def create_deck(scenarios: List[PreflopScenario], tags: List[str] = None) -> List[genanki.Deck]:
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
                f"{scenario.game} / {scenario.scenario} / {scenario.position}",
                scenario.game,
                scenario.scenario,
                scenario.position,
                ranges_txt,
                scenario.notes if scenario.notes else "",
                scenario.source if scenario.source else "",
                scenario.html_full(),
                scenario.html_top_left_quadrant_blank(),
                scenario.html_top_right_quadrant_blank(),
                scenario.html_bottom_left_quadrant_blank(),
                scenario.html_bottom_right_quadrant_blank(),
                scenario.extra_css(),
                scenario.html_legend(),
            ],
            tags=tags if tags else [],
        ))
    return deck

def write_deck_to_file(deck: genanki.Deck, filename: str):
    genanki.Package(deck).write_to_file(filename)
