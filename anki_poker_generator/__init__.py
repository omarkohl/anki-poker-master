import re
import random
from typing import Dict
from poker.hand import Range, Hand, Rank

_CSS_START = """<style>
    table.range, table.legend {
        border-collapse: collapse;
        font-size: 1em;
        font-family: monospace;
    }
    table.range td, table.legend td {
        border: 1px solid black;
        padding: 1px;
        text-align: center;
        width: 29px;
        height: 32px;
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
"""

_CSS_END = "</style>"

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
        "diagonal": "#F9F2D6",
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
    def __init__(self, ranges: Dict[str, Range], position: str, scenario: str, game: str, config: Dict = {}):
        self.ranges = ranges
        self.position = position
        self.scenario = scenario
        self.game = game

        self.config = {**_DEFAULT_CONFIG}
        for key, value in config.items():
            if key == "color":
                for color_k, color_v in value.items():
                    self.config["color"][_to_css_class(color_k)] = color_v
            else:
                self.config[key] = value

    def header(self) -> str:
        return f"<h1>{self.game}</h1><h2>{self.position}</h2><h3>{self.scenario}</h3>"

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
        css = _CSS_START
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
        for action in sorted(all_actions):
            css += f"td.{action} {{background-color: {color[action]};}}"
        css += f"td.blank.pair {{background-color: {color['diagonal']};}}"
        css += _CSS_END
        return css

    def html_legend(self) -> str:
        html = "<h2>Legend</h2>"
        html += "<table class='legend'>"
        all_actions = {"Fold"}
        all_actions.update(self.ranges.keys())
        for action in sorted(all_actions):
            html += f"<tr><th class='row'>{action}</th><td class='{_to_css_class(action)}'>&nbsp;</td></tr>"
        html += "<tr><th class='row'>Diagonal</th><td class='blank pair'>&nbsp;</td></tr>"
        html += "</table>"
        return html


def _to_html(action_ranges: Dict[str, Range]) -> str:
    html = ['<table class="range">']
    for row in reversed(Rank):
        html.append("<tr>")
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
            for a, r in action_ranges.items():
                if a == "blank":
                    # Handled later
                    continue
                if hand in r.hands:
                    action = a
            # Overwrite if blank
            if "blank" in action_ranges:
                if hand in action_ranges["blank"].hands:
                    action = "blank"
            html.append('<td class="%s %s">' % (_to_css_class(action), hand_type))
            html.append(str(hand))
            html.append("</td>")
        html.append("</tr>")
    html.append("</table>")
    return "".join(html)


def _to_css_class(action: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', action).lstrip('_').lower().strip()
