import re
import random
import copy
from typing import Dict, List
from poker.hand import Range, Hand, Rank
import schema
import yaml


# Note that there is overlap between the quadrants since the grid is 13x13.
# Each quadrant is 7x7.
_TOP_LEFT_QUADRANT = "98+, A8+, K8+, Q8+, J8+, T8+, 88+"
_TOP_RIGHT_QUADRANT = "A8s-, K8s-, Q8s-, J8s-, T8s-, 98s-, 87s-, 88"
_BOTTOM_LEFT_QUADRANT = "A8o-, K8o-, Q8o-, J8o-, T8o-, 98o-, 87o-, 88"
_BOTTOM_RIGHT_QUADRANT = "88-, 87-, 76-, 65-, 54-, 43-, 32-"

_DEFAULT_RANGE_COLORS = {
    "fold": "#D6D2D2",
    "call": "#4BE488",
    "raise": "#FF6A6A",
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
        range_colors: Dict = None,
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
        self.range_colors = copy.deepcopy(_DEFAULT_RANGE_COLORS)
        if range_colors is not None:
            for color_k, color_v in range_colors.items():
                self.range_colors[_to_css_class(color_k)] = color_v
        self.notes = notes
        self.source = source

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
        range_colors = self.range_colors.copy()
        available_colors = _EASY_TO_READ_COLORS.copy()
        for action in sorted(all_actions):
            if action not in range_colors:
                if available_colors:
                    range_colors[action] = available_colors.pop()
                else:
                    random.seed(action)
                    range_colors[action] = "#%06x" % random.randint(0, 0xFFFFFF)
        # We only need custom CSS if new actions are added or a default color is changed
        if range_colors == _DEFAULT_RANGE_COLORS:
            return ""
        indent = 0
        css = []
        for action in sorted(all_actions):
            css += [indent * " " + f"td.{action} {{"]
            indent += 4
            css += [indent * " " + f"background-color: {range_colors[action]};"]
            indent -= 4
            css += [indent * " " + "}"]
            css += [indent * " " + f"td.{action}.marked {{"]
            indent += 4
            css += [indent * " " + "background: repeating-linear-gradient("]
            indent += 4
            css += [indent * " " + "45deg,"]
            css += [
                indent * " " + f"{range_colors[action]}, {range_colors[action]} 3px,"
            ]
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


class _RangeSchema:
    def validate(self, data):
        if data is None:
            err_msg = "range can't be empty or null"
            raise schema.SchemaError(err_msg, err_msg)
        try:
            return Range(str(data))
        except ValueError:
            err_msg = f"'{data}' is an invalid range"
            raise schema.SchemaError(err_msg, err_msg)


def parse_scenario_yml(scenario_yml: str) -> List[PreflopScenario]:
    """
    Parse a YAML string containing scenarios and return a list of PreflopScenario objects.
    The input is assumed to be non-validated.
    """

    initial_schema = schema.Schema(
        schema.And(
            schema.Use(yaml.safe_load),
            [
                {
                    schema.Optional("DEFAULT"): bool,
                    schema.Optional("game"): str,
                    schema.Optional("position"): str,
                    schema.Optional("scenario"): str,
                    schema.Optional("ranges"): {str: _RangeSchema()},
                    schema.Optional("notes"): str,
                    schema.Optional("source"): str,
                    schema.Optional("range_colors"): {str: str},
                }
            ],
        )
    )
    default_scenario_values = {}
    default_found = False
    try:
        v_scenarios = initial_schema.validate(scenario_yml)
    except schema.SchemaError as e:
        raise ValidationError("error validating the scenarios file") from e
    for scenario in v_scenarios:
        if "DEFAULT" in scenario:
            if scenario["DEFAULT"]:
                if default_found:
                    raise ValidationError("There can only be one DEFAULT scenario.")
                default_found = True
                default_scenario_values = scenario
    if default_found:
        v_scenarios.remove(default_scenario_values)
        del default_scenario_values["DEFAULT"]

    for scenario in v_scenarios:
        for key, value in default_scenario_values.items():
            if key not in scenario:
                scenario[key] = value

    strict_schema = schema.Schema(
        [
            {
                "game": str,
                "position": str,
                "scenario": str,
                "ranges": {str: Range},
                schema.Optional("notes"): str,
                schema.Optional("source"): str,
                schema.Optional("range_colors"): {
                    str: schema.And(
                        str,
                        schema.Regex(
                            r"(^#[0-9A-Fa-f]{6}$)|(^[a-zA-Z]+$)",
                            error="'{}' is an invalid color",
                        ),
                    )
                },
            }
        ]
    )
    try:
        v_scenarios2 = strict_schema.validate(v_scenarios)
    except schema.SchemaError as e:
        raise ValidationError("error validating the scenarios file") from e

    for s in v_scenarios2:
        if "range_colors" in s:
            for action in s["range_colors"]:
                if action not in s["ranges"]:
                    raise ValidationError(
                        f"Range color defined for action '{action}', but no range is defined for that action."
                    )

    # validate that ranges within a scenario cannot overlap
    for s in v_scenarios2:
        for action in s["ranges"]:
            for other_action in s["ranges"]:
                if action == other_action:
                    continue
                hands1 = set(s["ranges"][action].hands)
                hands2 = set(s["ranges"][other_action].hands)
                if hands1.intersection(hands2):
                    raise ValidationError(
                        f"Range for action '{action}' overlaps with range "
                        + f"for action '{other_action}' in scenario "
                        + f"'{s['game']} / {s['scenario']} / {s['position']}'"
                    )

    return convert_scenarios(v_scenarios2)


def convert_scenarios(scenarios: Dict) -> List[PreflopScenario]:
    result = []
    for scenario in scenarios:
        game = scenario["game"]
        position = scenario["position"]
        scenario_name = scenario["scenario"]
        ranges = scenario["ranges"]
        notes = scenario.get("notes", None)
        source = scenario.get("source", None)
        range_colors = scenario.get("range_colors", None)
        result.append(
            PreflopScenario(
                game=game,
                position=position,
                scenario=scenario_name,
                ranges=ranges,
                range_colors=range_colors,
                notes=notes,
                source=source,
            ),
        )
    return result


class ValidationError(ValueError):
    def __init__(self, message):
        super().__init__(message)

    def humanize_error(self) -> str:
        err_msg = f"{self.args[0]}"
        if self.__cause__ and type(self.__cause__) == schema.SchemaError:
            err_msg += ": " + self.__cause__.code
        return err_msg
