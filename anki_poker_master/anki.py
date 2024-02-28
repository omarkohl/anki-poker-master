import random
import genanki
from importlib_resources import files
from anki_poker_master import PreflopScenario
from anki_poker_master.const import BLANK_TABLE, DEFAULT_CSS, DEFAULT_JS
from typing import List, Set, Tuple

_ALL_CARD_HEADER = """
<div class="row">
    <div class="column column_left">
        {{Tags}}
    </div>
    <div class="column column_right">
    </div>
</div>
<style>
{{CSS}}
</style>
""".lstrip()

_HEADER_FMT = (
    _ALL_CARD_HEADER
    + """
<b>Game: </b>{{Game}}
<br>
<b>Scenario: </b>{{Scenario}}
<br>
<b>Position: </b>{{Position}}
<br>
""".lstrip()
)


_ALL_CARD_FOOTER = (
    """
<p>
{{Ranges}}
</p>
{{#Notes}}
<p>
<small><b>Notes:</b></small>
<br>
<small>{{Notes}}</small>
</p>
{{/Notes}}
{{#Source}}
<p>
<small><b>Source:</b></small>
<br>
<small>{{Source}}</small>
</p>
{{/Source}}
<script>
""".lstrip()
    + DEFAULT_JS
    + "\n</script>"
)


_BASIC_HEADER = """
<div class="row">
    <div class="column column_left">
        {{Tags}}
    </div>
    <div class="column column_right">
    </div>
</div>
""".lstrip()

_BASIC_FOOTER = """
{{#Notes}}
<p>
<small><b>Notes:</b></small>
<br>
<small>{{Notes}}</small>
</p>
{{/Notes}}
{{#Source}}
<p>
<small><b>Source:</b></small>
<br>
<small>{{Source}}</small>
</p>
{{/Source}}
""".lstrip()

_BASIC_MODEL = genanki.Model(
    1708087674509,
    "Basic with source",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Notes"},
        {"name": "Source"},
    ],
    templates=[
        {
            "name": "QA",
            "qfmt": _BASIC_HEADER + "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}<br>" + _BASIC_FOOTER,
        },
    ],
    css=DEFAULT_CSS,
)


_SCENARIO_MODEL = genanki.Model(
    1995683082,  # Random number that should not change in the future
    "Poker Preflop Scenario",
    fields=[
        # The first field is just to avoid the 'Duplicate' warning in Anki
        # that checks for the first field.
        {"name": "Summary"},
        {"name": "Game"},
        {"name": "Scenario"},
        {"name": "Position"},
        {"name": "Ranges"},
        {"name": "Notes"},
        {"name": "Source"},
        {"name": "Full HTML", "collapsed": True},
        {"name": "Top Left Quadrant Blank HTML", "collapsed": True},
        {"name": "Top Right Quadrant Blank HTML", "collapsed": True},
        {"name": "Bottom Left Quadrant Blank HTML", "collapsed": True},
        {"name": "Bottom Right Quadrant Blank HTML", "collapsed": True},
        {"name": "CSS", "collapsed": True},
        {"name": "Legend", "collapsed": True},
    ],
    templates=[
        {
            "name": "Guess Position",
            "qfmt": _ALL_CARD_HEADER
            + "<style>{{CSS}}</style><b>Game: </b>{{Game}}<br>"
            + "<b>Scenario: </b>{{Scenario}}<br><b>Position: </b>?<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Game}} / {{Scenario}} / ?",
            "bafmt": "{{Position}}",
        },
        {
            "name": "Guess Scenario",
            "qfmt": _ALL_CARD_HEADER
            + "<style>{{CSS}}</style><b>Game: </b>{{Game}}<br>"
            + "<b>Scenario: </b>?<br><b>Position: </b>{{Position}}<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Game}} / ? / {{Position}}",
            "bafmt": "{{Scenario}}",
        },
        {
            "name": "TL Quadrant",
            "qfmt": _HEADER_FMT
            + "{{Top Left Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (top left)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "TR Quadrant",
            "qfmt": _HEADER_FMT
            + "{{Top Right Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (top right)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "BL Quadrant",
            "qfmt": _HEADER_FMT
            + "{{Bottom Left Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (bottom left)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "BR Quadrant",
            "qfmt": _HEADER_FMT
            + "{{Bottom Right Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (bottom right)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "Full",
            "qfmt": _HEADER_FMT
            + BLANK_TABLE
            + "<br>{{Legend}}"
            + "<script>"
            + DEFAULT_JS
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (full)",
            "bafmt": "(HTML table)",
        },
    ],
    css=DEFAULT_CSS,
)


def create_decks(
    scenarios: List[PreflopScenario],
    tags: List[str] = None,
) -> Tuple[List[genanki.Deck], Set[str]]:
    all_media_files = set()
    deck_standard = genanki.Deck(
        random.randrange(1 << 30, 1 << 31), "AnkiPokerMaster::Standard"
    )
    deck_detailed = genanki.Deck(
        random.randrange(1 << 30, 1 << 31), "AnkiPokerMaster::Detailed"
    )
    for scenario in scenarios:
        ranges_txt = ""
        for action in sorted(scenario.ranges):
            percentage = scenario.ranges[action].percent
            ranges_txt += (
                f"<b>{action}</b> ({percentage}%): {scenario.ranges[action]}<br>"
            )
        deck_standard.add_note(
            genanki.Note(
                model=_SCENARIO_MODEL,
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
            )
        )
        for range in scenario.ranges:
            for hand in scenario.ranges[range].hands:
                header = f"""
<style>
{scenario.extra_css()}
</style>
<b>Game: </b>{scenario.game}
<br>
<b>Scenario: </b>{scenario.scenario}
<br>
<b>Position: </b>{scenario.position}
<br>
<br>
""".lstrip()
                footer = f"""
<br>
{scenario.html_legend()}
<script>
{DEFAULT_JS}
</script>
""".lstrip()
                img1 = f"card-{hand.first}h.png"
                img2 = f"card-{hand.second}{'h' if hand.is_suited else 'c'}.png"
                all_media_files.add(img1)
                all_media_files.add(img2)
                question = (
                    header
                    + f"How should you play {hand}?<br>"
                    + f'<img src="{img1}">'
                    + f'<img src="{img2}">'
                )
                answer = (
                    f"You should <b>{range}</b>.<br><br>"
                    + scenario.html_full()
                    + footer
                )
                deck_detailed.add_note(
                    genanki.Note(
                        model=_BASIC_MODEL,
                        fields=[
                            question,
                            answer,
                            scenario.notes if scenario.notes else "",
                            scenario.source if scenario.source else "",
                        ],
                        tags=tags if tags else [],
                    )
                )
    return [deck_standard, deck_detailed], all_media_files


def write_deck_to_file(decks: List[genanki.Deck], media_files: Set[str], filename: str):
    media_files_full_path = []
    for media_file in media_files:
        image_path = files("anki_poker_master").joinpath("images", media_file)
        media_files_full_path.append(image_path)
    genanki.Package(decks, media_files_full_path).write_to_file(filename)
