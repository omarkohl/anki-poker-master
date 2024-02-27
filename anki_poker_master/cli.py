import os
import sys
import traceback
import argparse
import yaml
from importlib.metadata import version, PackageNotFoundError

from anki_poker_master import parse_scenario_yml, ValidationError
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
  source: "https://example.com/"

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
        "-o",
        "--output",
        type=str,
        help="Path to the resulting Anki package",
        default="./AnkiPokerMaster.apkg",
    )
    parser.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Write example files to the path specified by --config/-c or --scenarios/-s if and only if those files do not exist yet",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        type=str,
        help="Tags for the Anki decks. Specify multiple tags separated by spaces.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output (e.g. for debugging purposes)",
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

    try:
        with open(args.scenarios, "r") as f:
            scenarios = parse_scenario_yml(f.read(), config)
    except ValidationError as e:
        print(e.humanize_error())
        if args.verbose:
            print()
            traceback.print_exc()
        sys.exit(1)

    decks = create_decks(
        scenarios,
        args.tags,
    )
    if args.output.endswith(".apkg"):
        pkg_path = args.output
    else:
        pkg_path = f"{args.output}.apkg"
    if os.path.exists(pkg_path):
        print(f"The file {pkg_path} already exists.")
        sys.exit(1)
    # TODO needs to support multiple decks
    write_deck_to_file(decks[0], pkg_path)
