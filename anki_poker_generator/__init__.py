import re
import random
import copy
from typing import Dict
from poker.hand import Range, Hand, Rank

_CSS_START = """<style>
    table.range, table.legend {
        border-collapse: collapse;
        font-size: 0.7em;
        font-family: monospace;
    }
    table.range td, table.legend td {
        border: 1px solid black;
        padding: 1px;
        text-align: center;
        width: 25px;
        height: 25px;
        box-sizing: border-box;
        overflow: hidden;
    }
    td {
        background-color: white;
    }
    table.legend th {
        text-align: left;
        padding: 5px;
    }
    table.range td.pair {
        border: 2px solid black;
    }
    table.range td.center {
        font-weight: bold;
        font-size: 1.3em;
    }
"""

_CSS_END = "</style>\n"

# Note that there is overlap between the quadrants since the grid is 13x13.
# Each quadrant is 7x7.
_TOP_LEFT_QUADRANT = '98+, A8+, K8+, Q8+, J8+, T8+, 88+'
_TOP_RIGHT_QUADRANT = 'A8s-, K8s-, Q8s-, J8s-, T8s-, 98s-, 87s-, 88'
_BOTTOM_LEFT_QUADRANT = 'A8o-, K8o-, Q8o-, J8o-, T8o-, 98o-, 87o-, 88'
_BOTTOM_RIGHT_QUADRANT = '88-, 87-, 76-, 65-, 54-, 43-, 32-'

_DEFAULT_CONFIG = {
    "color": {
        "fold": "#D6D2D2",
        "call": "#4BE488",
        "raise": "#FF6A6A",
    }
}

_EASY_TO_READ_COLORS = [
    "#008000",  # Green
    "#FF0000",  # Red
    "#00FF00",  # Lime
    "#0000FF",  # Blue
    "#FFFF00",  # Yellow
    "#00FFFF",  # Aqua
    "#FF00FF",  # Fuchsia
    "#800000",  # Maroon
    "#000080",  # Navy
    "#808000",  # Olive
]


class PreflopScenario:
    def __init__(self, ranges: Dict[str, Range], position: str, scenario: str, game: str, config: Dict = None):
        self.ranges = ranges.copy()
        if "fold" not in [r.lower() for r in self.ranges]:
            # Make the fold range explicit if it's missing
            all_hands = Range("XX").hands
            fold_hands = set(all_hands)
            for action in self.ranges:
                fold_hands -= set(self.ranges[action].hands)
            fold_range = Range.from_objects(fold_hands)
            if len(fold_range) > 0:
                self.ranges["Fold"] = fold_range
        self.position = position
        self.scenario = scenario
        self.game = game
        self.config = copy.deepcopy(_DEFAULT_CONFIG)
        if config is not None:
            for key, value in config.items():
                if key == "color":
                    for color_k, color_v in value.items():
                        self.config["color"][_to_css_class(color_k)] = color_v
                else:
                    self.config[key] = value

    def header(self) -> str:
        indent = 0
        html = []
        html += [indent * " " + self.game + "<br>"]
        html += [indent * " " + "<b>Position: </b>%s<br>" % self.position]
        html += [indent * " " + "<b>Scenario: </b>%s<br>" % self.scenario]
        return "\n".join(html) + "\n"

    def html_full(self) -> str:
        return _to_html(self.ranges)

    def html_blank(self) -> str:
        return _to_html({"blank": Range("XX")})

    def _html_quadrant_blank(self, quadrant) -> str:
        ranges = self.ranges.copy()
        ranges["blank"] = Range(quadrant)
        return _to_html(ranges)

    def html_top_left_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_TOP_LEFT_QUADRANT)

    def html_top_right_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_TOP_RIGHT_QUADRANT)

    def html_bottom_left_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_BOTTOM_LEFT_QUADRANT)

    def html_bottom_right_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_BOTTOM_RIGHT_QUADRANT)

    def css(self) -> str:
        all_actions = {"fold"}
        for action in self.ranges:
            all_actions.add(_to_css_class(action))
        # Generate colors for actions that don't have a color
        color = self.config["color"].copy()
        available_colors = _EASY_TO_READ_COLORS.copy()
        for action in sorted(all_actions):
            if action not in color:
                if available_colors:
                    color[action] = available_colors.pop()
                else:
                    random.seed(action)
                    color[action] = "#%06x" % random.randint(0, 0xFFFFFF)
        indent = 0
        css = []
        indent += 4
        for action in sorted(all_actions):
            css += [indent * " " + f"td.{action} {{"]
            indent += 4
            css += [indent * " " + f"background-color: {color[action]};"]
            indent -= 4
            css += [indent * " " + "}"]
        indent -= 4
        return _CSS_START + "\n".join(css) + "\n" + _CSS_END

    def html_legend(self) -> str:
        indent = 0
        all_actions = {"Fold"}
        all_actions.update(self.ranges.keys())
        html = []
        html += [indent * " " + "<table class='legend'>"]
        indent += 4
        for action in sorted(all_actions):
            html.append(indent * " " + "<tr>")
            indent += 4
            html.append(indent * " " + f"<th class='row'>{action}</th>")
            html.append(indent * " " + f"<td class='{_to_css_class(action)}'>&nbsp;</td>")
            indent -= 4
            html.append(indent * " " + "</tr>")
        indent -= 4
        html.append(indent * " " + "</table>")
        return "\n".join(html) + "\n"


def _to_html(action_ranges: Dict[str, Range]) -> str:
    indent = 0
    html = [indent * " " + '<table class="range">']
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
                    action = "blank"
            css_classes = f"{_to_css_class(action)} {hand_type}"
            if hand == Hand("88"):
                css_classes += " center"
            html.append(
                indent * " " +
                '<td class="%s">%s</td>' % (
                    css_classes,
                    hand,
                ),
            )
        indent -= 4
        html.append(indent * " " + "</tr>")
    indent -= 4
    html.append(indent * " " + "</table>")
    return "\n".join(html) + "\n"


def _to_css_class(action: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', action).lstrip('_').lower().strip()
