import random
import genanki
from importlib_resources import files
import poker
from anki_poker_master import PreflopScenario
from anki_poker_master import helper
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
    + helper.default_js()
    + "</script>"
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
    "APM Basic",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Notes", "size": 14},
        {"name": "Source", "size": 14},
    ],
    templates=[
        {
            "name": "QA",
            "qfmt": _BASIC_HEADER + "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}<br>" + _BASIC_FOOTER,
            "bqfmt": "{{Question}}",
            "bafmt": "{{Answer}}",
        },
    ],
    css=helper.default_css(),
)


_SCENARIO_MODEL = genanki.Model(
    1995683082,  # Random number that should not change in the future
    "APM Preflop",
    fields=[
        # The first field is just to avoid the 'Duplicate' warning in Anki
        # that checks for the first field.
        {"name": "Summary"},
        {"name": "Game"},
        {"name": "Scenario"},
        {"name": "Position"},
        {"name": "Ranges"},
        {"name": "Notes", "size": 14},
        {"name": "Source", "size": 14},
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
            + helper.default_js()
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
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT + "{{Full HTML}}" + "<br>{{Legend}}" + _ALL_CARD_FOOTER,
            "bqfmt": "{{Game}} / ? / {{Position}}",
            "bafmt": "{{Scenario}}",
        },
        {
            "name": "TL Quadrant",
            "qfmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Top Left Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (top left)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "TR Quadrant",
            "qfmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Top Right Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (top right)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "BL Quadrant",
            "qfmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Bottom Left Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (bottom left)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "BR Quadrant",
            "qfmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Bottom Right Quadrant Blank HTML}}"
            + "<br>{{Legend}}"
            + "<script>"
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT
            + "<br>Fill in the blank<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (bottom right)",
            "bafmt": "(HTML table)",
        },
        {
            "name": "Full",
            "qfmt": _HEADER_FMT
            + "<br>Fill in the blank (entire table)<br>"
            + helper.blank_table()
            + "<br>{{Legend}}"
            + "<script>"
            + helper.default_js()
            + "</script>",
            "afmt": _HEADER_FMT
            + "<br>Fill in the blank (entire table)<br>"
            + "{{Full HTML}}"
            + "<br>{{Legend}}"
            + _ALL_CARD_FOOTER,
            "bqfmt": "{{Summary}} (full)",
            "bafmt": "(HTML table)",
        },
    ],
    css=helper.default_css(),
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
        header_basic_model = f"""
<b>Game: </b>{scenario.game}
<br>
<b>Scenario: </b>{scenario.scenario}
<br>
<b>Position: </b>{scenario.position}
<br>
<br>
""".lstrip()
        if scenario.extra_css():
            # prepend the extra CSS
            header_basic_model = (
                f"<style>\n{scenario.extra_css()}\n</style>" + header_basic_model
            )

        # Note that 2Xs and 2Xo are not included because there are no lower
        # hands than them
        for c in [
            "AXs",
            "KXs",
            "QXs",
            "JXs",
            "TXs",
            "9Xs",
            "8Xs",
            "7Xs",
            "6Xs",
            "5Xs",
            "4Xs",
            "3Xs",
            "AXo",
            "KXo",
            "QXo",
            "JXo",
            "TXo",
            "9Xo",
            "8Xo",
            "7Xo",
            "6Xo",
            "5Xo",
            "4Xo",
            "3Xo",
            "pairs",
        ]:
            if c == "pairs":
                img1 = f"apm-card-Xh.png"
                img2 = f"apm-card-Xc.png"
                question = "How should you play pairs?"
            else:
                img1 = f"apm-card-{c[0]}h.png"
                img2 = f"apm-card-{c[1]}{'h' if c[2] == 's' else 'c'}.png"
                if c[0] == "A":
                    # In this case it's obvious that there is no higher card
                    question = f"How should you play {c}?"
                else:
                    question = f"How should you play {c} (where {c[0]} is higher)?"
            all_media_files.add(img1)
            all_media_files.add(img2)
            full_question = (
                header_basic_model
                + question
                + "<div class='row'>"
                + f'<img src="{img1}">'
                + f'<img src="{img2}">'
                + "</div>"
            )
            answer = _get_row_question_answer(c, scenario.ranges)
            notes = (scenario.notes + "<br>\n") if scenario.notes else ""
            notes += scenario.html_full() + "<br>" + scenario.html_legend()
            deck_standard.add_note(
                genanki.Note(
                    model=_BASIC_MODEL,
                    fields=[
                        full_question,
                        answer,
                        notes,
                        scenario.source if scenario.source else "",
                    ],
                    tags=tags if tags else [],
                )
            )
        for range in scenario.ranges:
            for hand in scenario.ranges[range].hands:
                img1 = f"apm-card-{hand.first}h.png"
                img2 = f"apm-card-{hand.second}{'h' if hand.is_suited else 'c'}.png"
                all_media_files.add(img1)
                all_media_files.add(img2)
                full_question = (
                    header_basic_model
                    + f"How should you play {hand}?"
                    + "<div class='row'>"
                    + f'<img src="{img1}">'
                    + f'<img src="{img2}">'
                    + "</div>"
                )
                answer = f"You should <b>{range}</b>."
                notes = (scenario.notes + "<br>\n") if scenario.notes else ""
                notes += scenario.html_full() + "<br>" + scenario.html_legend()
                deck_detailed.add_note(
                    genanki.Note(
                        model=_BASIC_MODEL,
                        fields=[
                            full_question,
                            answer,
                            notes,
                            scenario.source if scenario.source else "",
                        ],
                        tags=tags if tags else [],
                    )
                )
    return [deck_standard, deck_detailed], all_media_files


def write_deck_to_file(decks: List[genanki.Deck], media_files: Set[str], filename: str):
    media_files_full_path = []
    for media_file in media_files:
        image_path = files("anki_poker_master").joinpath(
            "resources", "images", media_file
        )
        media_files_full_path.append(image_path)
    genanki.Package(decks, media_files_full_path).write_to_file(filename)


def _get_row_question_answer(hand: str, ranges: dict) -> str:
    """
    hand is a string like "AXs", "AXo" or "77", that's why it's a "row question"
    because it refers to a single row (or column) in the table. Note also that
    we are only interested in the part of the row (column) that lies to the left
    (below) the pair diagonal.
    For this row we want to know what the correct action is, given the ranges.
    """
    range_keys = sorted([k for k in ranges])
    ranges_new = {k: set() for k in range_keys}
    if hand == "pairs":
        potential_hands = poker.PAIR_HANDS
    else:
        # Only lower than the pair e.g. for KXs, only lower than KK
        limit = poker.Hand(2 * hand[0])
        potential_hands = [h for h in poker.Range(hand).hands if h < limit]
    for k in range_keys:
        for h in potential_hands:
            if h in ranges[k].hands:
                ranges_new[k].add(h)

    answer_ranges = {}
    for k in range_keys:
        r_summarized = poker.Range.from_objects(ranges_new[k])
        if len(r_summarized.hands) == 0:
            continue
        elif len(r_summarized.hands) < 4:
            answer_ranges[k] = ", ".join(str(h) for h in r_summarized.hands)
        else:
            answer_ranges[k] = r_summarized
    result = []
    if len(answer_ranges) == 1:
        k = list(answer_ranges.keys())[0]
        result.append(f"<b>{k}:</b> All ({answer_ranges[k]})")
    else:
        for k in answer_ranges:
            result.append(f"<b>{k}:</b> {answer_ranges[k]}")
    return "<br>".join(result)
