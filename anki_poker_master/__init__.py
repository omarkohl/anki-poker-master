import re
import random
import copy
from typing import Dict, List
from poker.hand import Range, Hand, Rank
import strictyaml


# Note that there is overlap between the quadrants since the grid is 13x13.
# Each quadrant is 7x7.
_TOP_LEFT_QUADRANT = "98+, A8+, K8+, Q8+, J8+, T8+, 88+"
_TOP_RIGHT_QUADRANT = "A8s-, K8s-, Q8s-, J8s-, T8s-, 98s-, 87s-, 88"
_BOTTOM_LEFT_QUADRANT = "A8o-, K8o-, Q8o-, J8o-, T8o-, 98o-, 87o-, 88"
_BOTTOM_RIGHT_QUADRANT = "88-, 87-, 76-, 65-, 54-, 43-, 32-"

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
    def __init__(
        self,
        ranges: Dict[str, Range],
        position: str,
        scenario: str,
        game: str,
        config: Dict = None,
        notes: str = None,
        source: str = None,
    ):
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
        self.source = source
        self.notes = notes

    def html_full(self) -> str:
        return _to_html(self.ranges)

    def html_blank(self) -> str:
        return _to_html({"blank": Range("XX")}, table_css_classes=["markable"])

    def _html_quadrant_blank(self, quadrant) -> str:
        ranges = self.ranges.copy()
        ranges["blank"] = Range(quadrant)
        return _to_html(ranges, table_css_classes=["markable"])

    def html_top_left_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_TOP_LEFT_QUADRANT)

    def html_top_right_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_TOP_RIGHT_QUADRANT)

    def html_bottom_left_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_BOTTOM_LEFT_QUADRANT)

    def html_bottom_right_quadrant_blank(self) -> str:
        return self._html_quadrant_blank(_BOTTOM_RIGHT_QUADRANT)

    def extra_css(self) -> str:
        """
        Generate custom CSS for the ranges, if needed. This is only the case
        if new actions are added or a default color is changed. Otherwise,
        an empty string is returned.
        """
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
        # We only need custom CSS if new actions are added or a default color is changed
        if color == _DEFAULT_CONFIG["color"]:
            return ""
        indent = 0
        css = []
        for action in sorted(all_actions):
            css += [indent * " " + f"td.{action} {{"]
            indent += 4
            css += [indent * " " + f"background-color: {color[action]};"]
            indent -= 4
            css += [indent * " " + "}"]
            css += [indent * " " + f"td.{action}.marked {{"]
            indent += 4
            css += [indent * " " + "background: repeating-linear-gradient("]
            indent += 4
            css += [indent * " " + "45deg,"]
            css += [indent * " " + f"{color[action]}, {color[action]} 3px,"]
            css += [indent * " " + f"#00000070 3px, #00000070 6px"]
            indent -= 4
            css += [indent * " " + ");"]
            indent -= 4
            css += [indent * " " + "}"]
        return "\n".join(css) + "\n"

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
            html.append(
                indent * " " + f"<td class='{_to_css_class(action)}'>&nbsp;</td>"
            )
            indent -= 4
            html.append(indent * " " + "</tr>")
        indent -= 4
        html.append(indent * " " + "</table>")
        return "\n".join(html) + "\n"


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
            css_classes = f"{_to_css_class(action)} {hand_type}" + (
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


def _to_css_class(action: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", action).lstrip("_").lower().strip()


def parse_scenario_yml(scenario_yml: str, config: Dict) -> List[PreflopScenario]:
    """
    Parse a YAML string containing scenarios and return a list of PreflopScenario objects.
    The input is assumed to be non-validated.
    """
    """
    scenarios_schema = schema.Schema(
        schema.And(
            schema.Use(yaml.safe_load),
            [
                {
                    "game": str,
                    "position": str,
                    "scenario": str,
                    "ranges": {str: str},
                    schema.Optional("notes"): str,
                    schema.Optional("source"): str,
                    schema.Optional("range_colors"): {str: str},
                }
            ],
        )
    )
    """
    initial_schema = strictyaml.Seq(
        strictyaml.Map(
            {
                strictyaml.Optional("DEFAULT"): strictyaml.Bool(),
                strictyaml.Optional("game"): strictyaml.Str(),
                strictyaml.Optional("position"): strictyaml.Str(),
                strictyaml.Optional("scenario"): strictyaml.Str(),
                strictyaml.Optional("ranges"): strictyaml.MapPattern(
                    strictyaml.Str(), strictyaml.Str()
                ),
                strictyaml.Optional("notes"): strictyaml.Str(),
                strictyaml.Optional("source"): strictyaml.Str(),
                strictyaml.Optional("range_colors"): strictyaml.MapPattern(
                    strictyaml.Str(), strictyaml.Str()
                ),
            }
        )
    )
    v_scenarios = strictyaml.load(scenario_yml, initial_schema).data

    default_values = {}
    default_found = False
    for scenario in v_scenarios:
        if scenario.get("DEFAULT", False):
            if default_found:
                raise ValueError("There can only be one DEFAULT scenario.")
            default_found = True
            default_values = scenario

    if default_found:
        v_scenarios.remove(default_values)
        del default_values["DEFAULT"]

    for scenario in v_scenarios:
        for key, value in default_values.items():
            if key not in scenario:
                scenario[key] = value

    strict_schema = strictyaml.Seq(
        strictyaml.Map(
            {
                "game": strictyaml.Str(),
                "position": strictyaml.Str(),
                "scenario": strictyaml.Str(),
                "ranges": strictyaml.MapPattern(strictyaml.Str(), strictyaml.Str()),
                strictyaml.Optional("notes"): strictyaml.Str(),
                strictyaml.Optional("source"): strictyaml.Str(),
                strictyaml.Optional("range_colors"): strictyaml.MapPattern(
                    strictyaml.Str(), strictyaml.Str()
                ),
            }
        )
    )
    v_scenarios2 = strictyaml.as_document(v_scenarios, strict_schema)

    for s in v_scenarios2:
        if "range_colors" in s:
            for action in s["range_colors"]:
                if action not in s["ranges"]:
                    raise ValueError(
                        f"Range color defined for action '{action}', but no range is defined for that action."
                    )

    return convert_scenarios(v_scenarios2.data, config)


def convert_scenarios(scenarios: Dict, config: Dict) -> List[PreflopScenario]:
    result = []
    for scenario in scenarios:
        game = scenario["game"]
        position = scenario["position"]
        scenario_name = scenario["scenario"]
        ranges = scenario["ranges"]
        notes = scenario.get("notes", None)
        source = scenario.get("source", None)
        result.append(
            PreflopScenario(
                game=game,
                position=position,
                scenario=scenario_name,
                ranges=convert_ranges(ranges),
                config=config,
                notes=notes,
                source=source,
            ),
        )
    return result


def convert_ranges(ranges: Dict) -> Dict[str, Range]:
    result = {}
    for action, range_str in ranges.items():
        result[action] = Range(range_str)
    return result
