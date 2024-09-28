from typing import List, Dict

import schema
import yaml
from poker import Range

from anki_poker_master.model import ValidationError, PreflopScenario


def parse_scenario_yml(scenario_yml: str) -> List[PreflopScenario]:
    """
    Parse a YAML string containing scenarios and return a list of PreflopScenario objects.
    The input is assumed to be non-validated.
    """

    color_schema = schema.And(
        str,
        schema.Regex(
            r"(^#[0-9A-Fa-f]{6}$)|(^[a-zA-Z]+$)",
            error="'{}' is an invalid color",
        ),
    )

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
                    schema.Optional("notes"): schema.Use(
                        lambda x: "" if x is None else str(x)
                    ),
                    schema.Optional("source"): schema.Use(
                        lambda x: "" if x is None else str(x)
                    ),
                    schema.Optional("range_colors"): {
                        str: schema.Or(
                            color_schema,
                            schema.And([color_schema], lambda x: len(x) == 2),
                        )
                    },
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
                schema.Optional("range_colors"): object,
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
        range_colors = {}
        for k in scenario.get("range_colors", {}):
            if isinstance(scenario["range_colors"][k], str):
                range_colors[k] = (
                    scenario["range_colors"][k],
                    scenario["range_colors"][k],
                )
            else:
                range_colors[k] = scenario["range_colors"][k]
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


EXAMPLE_SCENARIO_FILE = """
## The scenario file is a list of scenarios. Each scenario is a dictionary
## with the following keys: game, position, scenario, ranges, range_colors,
## notes and source.
## ranges is a dictionary of ranges you want to differentiate. Most common
## is to have Raise, Call and Fold. You can also have custom range names.
## All hands that are not specified will default to 'Fold'.

- game: "Cash 100BB 6P"
  position: "LJ"
  scenario: "Opening"
  ranges:
    Raise: "A2s+, K5s+, Q9s+, JTs, T9s, ATo+, KJo+, QJo+, 77+"
  source: pokertrainer.se

- game: "Cash 100BB 6P"
  position: "HJ"
  scenario: "Opening"
  ranges:
    Raise: "A2s+, K5s+, Q8s+, J9s+, T9s, A9o+, KTo+, QTo+, 66+"
  source: pokertrainer.se

# - game: "Cash 100BB 6P"
#   position: "CO"
#   scenario: "raise from LJ"
#   ranges:
#     Raise: "A9s+, KTs+, QJs, A5s, A4s, AQo+, KQo, TT+"
#   notes: "This is a note for the scenario. You can write anything here."
## You can specify the source of you Poker ranges. The default is empty.
## This can be useful if after a few months you want to check the source
## again or if you encounter contradictory information somewhere. Use HTML
## to format the source.
#source: >
#  Chapter 16<br>
#  Big Important Poker Book<br>
#  John Smith<br>
#
## You can specify one default scenario that sets the default values for all
## fields that are not specified in the other scenarios.
# - DEFAULT: true
#   source: "https://example.com/"
#   game: "Cash 100BB 6P"
#
## As you can see in the following example, you are very flexible in how you
## can define the information you care about.
# - game: "Las Vegas Tournament 22"
#   position: "Under the gun"
#   scenario: "Facing a 3bet"
#   ranges:
#     Raise: "A2s+"
#     Call: "77+"
#     "Secret range to bluff against Bob": "66-"
#   # You can (but don't have to!) specify the color of the ranges.
#   range_colors:
#     "Secret range to bluff against Bob": "#A7FF12"
#     Raise:
#       # You can specify two colors, the first to use for light mode and the
#       # second for dark mode.
#       - lightblue
#       - darkblue
#   notes: "Remember that Bob always folds to 3bets."
#
## ... and so on
""".lstrip()


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
