import random
from typing import List, Tuple, Set, Dict

import genanki
import poker
from importlib_resources import files
from poker import Range, Rank, Hand

from anki_poker_master import helper
from anki_poker_master.helper import str_to_css_class
from anki_poker_master.model import PreflopScenario
from anki_poker_master.presenter.anki import BASIC_MODEL

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
# CSS above is duplicate, no??


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
                    html_full(scenario),
                    html_top_left_quadrant_blank(scenario),
                    html_top_right_quadrant_blank(scenario),
                    html_bottom_left_quadrant_blank(scenario),
                    html_bottom_right_quadrant_blank(scenario),
                    extra_css(scenario.extra_range_colors, scenario),
                    html_legend(scenario),
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
        if extra_css(scenario.extra_range_colors, scenario):
            # prepend the extra CSS
            header_basic_model = (
                f"<style>\n{extra_css(scenario.extra_range_colors, scenario)}\n</style>" + header_basic_model
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
            notes += html_full(scenario) + "<br>" + html_legend(scenario)
            deck_standard.add_note(
                genanki.Note(
                    model=BASIC_MODEL,
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
                notes += html_full(scenario) + "<br>" + html_legend(scenario)
                deck_detailed.add_note(
                    genanki.Note(
                        model=BASIC_MODEL,
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


def html_full(scenario: PreflopScenario) -> str:
    return _to_html(scenario.ranges)


def html_blank() -> str:
    return _to_html({"blank": Range("XX")}, table_css_classes=["markable"])


def _html_quadrant_blank(scenario: PreflopScenario, quadrant) -> str:
    ranges = scenario.ranges.copy()
    ranges["blank"] = Range(quadrant)
    return _to_html(ranges, table_css_classes=["markable"])


def html_top_left_quadrant_blank(scenario: PreflopScenario) -> str:
    return _html_quadrant_blank(scenario, _TOP_LEFT_QUADRANT)


def html_top_right_quadrant_blank(scenario: PreflopScenario) -> str:
    return _html_quadrant_blank(scenario, _TOP_RIGHT_QUADRANT)


def html_bottom_left_quadrant_blank(scenario: PreflopScenario) -> str:
    return _html_quadrant_blank(scenario, _BOTTOM_LEFT_QUADRANT)


def html_bottom_right_quadrant_blank(scenario: PreflopScenario) -> str:
    return _html_quadrant_blank(scenario, _BOTTOM_RIGHT_QUADRANT)


def extra_css(extra_range_colors, scenario: PreflopScenario) -> str:
    """
    Generate custom CSS for the ranges, if needed. This is only the case
    if new actions are added or a default color is changed. Otherwise,
    an empty string is returned.
    """
    default_actions = {"raise", "fold", "call"}
    # Generate colors for actions that don't have a color
    range_colors = extra_range_colors.copy()
    available_colors = _EASY_TO_READ_COLORS.copy()
    for action in [str_to_css_class(a) for a in scenario.ranges.keys()]:
        # if it's a default action and it's not in the range_colors then
        # nothing needs to be done -> covered by default CSS.
        # If it's a default action and it's in range_colors then it will
        # already be overwritten so nothing else needs to be done
        # If it's not a default action and it's in range colors then it will
        # also be written to the CSS.
        # If it's not a default action and it's not in range colors then we
        # need to choose a color.
        if action not in default_actions and action not in range_colors:
            if available_colors:
                range_colors[action] = available_colors.pop()
            else:
                random.seed(action)
                color_light = "#%06x" % random.randint(0, 0xFFFFFF)
                color_dark = "#%06x" % random.randint(0, 0xFFFFFF)
                range_colors[action] = (color_light, color_dark)
    # We only need custom CSS if new actions are added or a default color is changed
    if not range_colors:
        return ""
    indent = 0
    css = []
    for action in sorted(range_colors.keys()):
        color_light, color_dark = range_colors[action]
        css += [indent * " " + f"table.range td.{action}, table.legend td.{action} {{"]
        indent += 4
        css += [indent * " " + f"background-color: {color_light};"]
        indent -= 4
        css += [indent * " " + "}"]

        css += [indent * " " + f".nightMode table.range td.{action}, .nightMode table.legend td.{action} {{"]
        indent += 4
        css += [indent * " " + f"background-color: {color_dark};"]
        indent -= 4
        css += [indent * " " + "}"]

        css += [indent * " " + f"table.range td.{action}.marked, table.legend td.{action}.marked {{"]
        indent += 4
        css += [indent * " " + "background: repeating-linear-gradient("]
        indent += 4
        css += [indent * " " + "45deg,"]
        css += [indent * " " + f"{color_light}, {color_light} 3px,"]
        css += [indent * " " + f"#00000070 3px, #00000070 6px"]
        indent -= 4
        css += [indent * " " + ");"]
        indent -= 4
        css += [indent * " " + "}"]

        css += [indent * " " + f".nightMode table.range td.{action}.marked, .nightMode table.legend td.{action}.marked {{"]
        indent += 4
        css += [indent * " " + "background: repeating-linear-gradient("]
        indent += 4
        css += [indent * " " + "45deg,"]
        css += [indent * " " + f"{color_dark}, {color_dark} 3px,"]
        css += [indent * " " + f"#00000070 3px, #00000070 6px"]
        indent -= 4
        css += [indent * " " + ");"]
        indent -= 4
        css += [indent * " " + "}"]

    return "\n".join(css) + "\n"


def html_legend(scenario: PreflopScenario) -> str:
    indent = 0
    all_actions = {"Fold"}
    all_actions.update(scenario.ranges.keys())
    html = []
    html += [indent * " " + "<table class='legend'>"]
    indent += 4
    for action in sorted(all_actions):
        html.append(indent * " " + "<tr>")
        indent += 4
        html.append(indent * " " + f"<th class='row'>{action}</th>")
        html.append(
            indent * " " + f"<td class='{str_to_css_class(action)}'>&nbsp;</td>"
        )
        indent -= 4
        html.append(indent * " " + "</tr>")
    indent -= 4
    html.append(indent * " " + "</table>")
    return "\n".join(html) + "\n"


# Note that there is overlap between the quadrants since the grid is 13x13.
# Each quadrant is 7x7.
_TOP_LEFT_QUADRANT = "98+, A8+, K8+, Q8+, J8+, T8+, 88+"
_TOP_RIGHT_QUADRANT = "A8s-, K8s-, Q8s-, J8s-, T8s-, 98s-, 87s-, 88"
_BOTTOM_LEFT_QUADRANT = "A8o-, K8o-, Q8o-, J8o-, T8o-, 98o-, 87o-, 88"
_BOTTOM_RIGHT_QUADRANT = "88-, 87-, 76-, 65-, 54-, 43-, 32-"

# These colors are used in inverted order i.e. the last one will be chosen
# first.
# The first color in each tuple is the one to use for light mode the second one
# is for dark mode.
_EASY_TO_READ_COLORS = [
    ("#F0AC54", "#8A5317"),  # Orange (light)
    ("#5E5EF3", "#2E2E9A"),  # Blue (light)
    ("#C24F4F", "#7A2D2D"),  # Brown (light)
    ("#008000", "#004000"),  # Green (light)
    ("#FF0000", "#800000"),  # Red (light)
    ("#00FF00", "#008000"),  # Lime (light)
    ("#FFFF00", "#808000"),  # Yellow (light)
    ("#00FFFF", "#015757"),  # Aqua (light)
    ("#FF00FF", "#800080"),  # Fuchsia (light)
    ("#808000", "#404000"),  # Olive (light)
]


def _to_html(
    action_ranges: Dict[str, Range], table_css_classes: List[str] = None
) -> str:
    table_classes = {"range"}
    if table_css_classes:
        table_classes.update(c.lower() for c in table_css_classes)
    indent = 0
    html = [indent * " " + f'<table class="{" ".join(sorted(table_classes))}">']
    indent += 4
    for row in reversed(Rank):
        html.append(indent * " " + "<tr>")
        indent += 4
        for col in reversed(Rank):
            if row > col:
                suit = "s"
                hand_type = "suited"
            elif row < col:
                suit = "o"
                hand_type = "offsuit"
            else:
                suit = ""
                hand_type = "pair"
            action = "fold"
            blank = False
            hand = Hand(row.val + col.val + suit)
            for a in sorted(action_ranges):
                if a == "blank":
                    # Handled later
                    continue
                if hand in action_ranges[a].hands:
                    action = a
            # Overwrite if blank
            if "blank" in action_ranges:
                if hand in action_ranges["blank"].hands:
                    blank = True
            css_classes = f"{str_to_css_class(action)} {hand_type}" + (
                " blank" if blank else ""
            )
            if hand == Hand("88"):
                css_classes += " center"
            html.append(
                indent * " "
                + '<td class="%s">%s</td>'
                % (
                    css_classes,
                    hand,
                ),
            )
        indent -= 4
        html.append(indent * " " + "</tr>")
    indent -= 4
    html.append(indent * " " + "</table>")
    return "\n".join(html) + "\n"
