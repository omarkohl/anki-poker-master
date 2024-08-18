import os
import sys
import traceback
import argparse
from importlib.metadata import version, PackageNotFoundError

from anki_poker_master.preflop_scenario import parse_scenario_yml, ValidationError, EXAMPLE_SCENARIO_FILE
from anki_poker_master.anki import create_decks, write_deck_to_file


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
