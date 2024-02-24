import os
import sys
from poker.hand import Range
from typing import Dict, List
import argparse
import yaml
from importlib.metadata import version, PackageNotFoundError

from anki_poker_master import PreflopScenario
from anki_poker_master.anki import create_decks, write_deck_to_file


EXAMPLE_CONFIG_FILE = """
## You can override the default colors for the ranges and specify colors for
## custom ranges.
#color:
#  - Fold: '#D6D2D2'
#  - Call: '#4BE488'
#  - Raise: '#FF6A6A'
#  - My custom range: 'darkblue'
#
## Choose which deck types you want to generate. The default is 'overview' and
## 'ranks' only.
## - The 'overview' contains the range tables and asks you to memorize them
##   visually. It also contains some general information about the ranges.
## - The 'ranks' deck contains questions of the type "You are opening as BTN
##   in a 6P 100BB cash game. Which AXs do you play and how?".
## - The 'combinations' deck generates all 169 possible combinations of two
##   Poker cards and asks for each one if you should play it and how. Beware
##   that this will generate a lot of Anki cards!
#deck_types:
#  - overview: True
#  - ranks: True
#  - combinations: False
#
## If you decide to generate multiple deck types, you can merge them into one
## Anki deck. The default is False (i.e. you will get one Anki deck per deck
## type).
#merge_decks: False
#
## You can specify a custom deck name. The default is "Poker Ranges". If you
## generate multiple deck types, the deck name will be suffixed with the deck
## type.
#deck_name: "Poker Ranges"
#
## You can specify the source of you Poker ranges. The default is empty.
## This can be useful if after a few months you want to check the source
## again or if you encounter contradictory information somewhere. Use HTML
## to format the source.
#source: >
#  Chapter 16<br>
#  Big Important Poker Book<br>
#  John Smith<br>
#
## You can specify the Anki tags you want to add to the generated cards. The
## default is an empty list.
#tags: ["poker"]
#
""".lstrip()

EXAMPLE_SCENARIO_FILE = """
## The scenario file is a list of scenarios. Each scenario is a dictionary
## with the following keys: game, position, scenario, ranges and
## notes (optional).
## ranges is a dictionary of ranges you want to differentiate. Most common
## is to have Raise, Call and Fold. You can also have custom range names.
## Everything that is not specified will default to 'Fold'.

- game: "Cash 100BB 6P"
  position: "BTN"
  scenario: "Opening"
  ranges:
    Raise: "A2s+, K2s+, Q2s+, J4s+, T6s+, 96s+, 86s+, 75s+, 65s+, 54s+, A3o+, K8o+, Q9o+, J9o+, T9o+, 22+"

# - game: "Cash 100BB 6P"
#   position: "CO"
#   scenario: "raise from LJ"
#   ranges:
#     Raise: "A9s+, KTs+, QJs, A5s, A4s, AQo+, KQo, TT+"
#   notes: "This is a note for the scenario. You can write anything here."

## As you can see in the following example, you are very flexible in how you
## can define the information you care about.
# - game: "Las Vegas Tournament 22"
#   position: "Under the gun"
#   scenario: "Facing a 3bet"
#   ranges:
#     Raise: "A2s+"
#     Call: "77+"
#     "Secret range to bluff against Bob": "66-"
#   notes: "Remember that Bob is a nit and always folds to 3bets."

## ... and so on
""".lstrip()


def main():
    main_with_args(sys.argv[1:])


def main_with_args(args):
    try:
        package_version = version("anki-poker-master")
    except PackageNotFoundError:
        # package is not installed
        package_version = "dev"

    parser = argparse.ArgumentParser(
        description="AnkiPokerMaster - Create Anki decks for poker ranges"
    )
    parser.add_argument(
        "-c", "--config", type=str, help="Path to the configuration file"
    )
    parser.add_argument(
        "-s", "--scenarios", type=str, help="Path to the scenarios file"
    )
    parser.add_argument(
        "-d", "--output-dir", type=str, help="Path to the output directory", default="."
    )
    parser.add_argument("-n", "--name", type=str, help="Name of the Anki deck")
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Write example files to the path specified by --config/-c or --scenarios/-s if and only if those files do not exist yet",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"AnkiPokerMaster {package_version}",
    )
    args = parser.parse_args(args)

    if args.example:
        if not args.config and not args.scenarios:
            print(
                "You need to specify either --config/-c or --scenarios/-s to write example files."
            )
            return
        if args.config:
            if os.path.exists(args.config):
                print(f"The file {args.config} already exists.")
                sys.exit(1)
            with open(args.config, "w") as f:
                f.write(EXAMPLE_CONFIG_FILE)
            print(f"Example configuration file written to {args.config}")
        if args.scenarios:
            if os.path.exists(args.scenarios):
                print(f"The file {args.scenarios} already exists.")
                sys.exit(1)
            with open(args.scenarios, "w") as f:
                f.write(EXAMPLE_SCENARIO_FILE)
            print(f"Example scenarios file written to {args.scenarios}")
        return

    config = {}
    if args.config:  # parse as yaml
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

    if not args.scenarios:
        print(
            "You need to specify a scenarios file. You can use --example to create an example file."
        )
        sys.exit(1)

    with open(args.scenarios, "r") as f:
        scenarios = yaml.safe_load(f)

    decks = create_decks(
        convert_scenarios(scenarios, config),
        tags=config.get("tags", None),
        deck_name=config.get("deck_name", "Poker Ranges"),
    )
    deck_name = config.get("deck_name", "Poker Ranges")
    deck_path = os.path.join(args.output_dir, f"{deck_name}.apkg")
    # TODO needs to support multiple decks
    write_deck_to_file(decks[0], deck_path)


def convert_scenarios(scenarios: Dict, config: Dict) -> List[PreflopScenario]:
    result = []
    for scenario in scenarios:
        game = scenario["game"]
        position = scenario["position"]
        scenario_name = scenario["scenario"]
        ranges = scenario["ranges"]
        notes = scenario.get("notes", None)
        result.append(
            PreflopScenario(
                game=game,
                position=position,
                scenario=scenario_name,
                ranges=convert_ranges(ranges),
                config=config,
                notes=notes,
            ),
        )
    return result


def convert_ranges(ranges: Dict) -> Dict[str, Range]:
    result = {}
    for action, range_str in ranges.items():
        result[action] = Range(range_str)
    return result
