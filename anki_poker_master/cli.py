import os
import sys
import traceback
import argparse
import yaml
from importlib.metadata import version, PackageNotFoundError

from anki_poker_master import parse_scenario_yml, ValidationError
from anki_poker_master.anki import create_decks, write_deck_to_file


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
        help="Write example file to the path specified by --scenarios/-s if and only if the file does not exist yet",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        type=str,
        help="Tags for the Anki decks. Specify multiple tags separated by "
        + "spaces. Default is a single tag: poker.",
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
        if not args.scenarios:
            print("You need to specify --scenarios/-s to write an exampl file.")
            return
        if os.path.exists(args.scenarios):
            print(f"The file {args.scenarios} already exists.")
            sys.exit(1)
        with open(args.scenarios, "w") as f:
            f.write(EXAMPLE_SCENARIO_FILE)
        print(f"Example scenarios file written to {args.scenarios}")
        return

    if not args.scenarios:
        print(
            "You need to specify a scenarios file. You can use --example to create an example file."
        )
        sys.exit(1)

    try:
        with open(args.scenarios, "r") as f:
            scenarios = parse_scenario_yml(f.read())
    except ValidationError as e:
        print(e.humanize_error())
        if args.verbose:
            print()
            traceback.print_exc()
        sys.exit(1)

    if args.tags is None:
        tags = ["poker"]
    else:
        tags = args.tags.copy()

    if args.output.endswith(".apkg"):
        pkg_path = args.output
    else:
        pkg_path = f"{args.output}.apkg"
    if os.path.exists(pkg_path):
        print(f"The file {pkg_path} already exists.")
        sys.exit(1)

    decks, media_files = create_decks(
        scenarios,
        tags,
    )
    write_deck_to_file(decks, media_files, pkg_path)
