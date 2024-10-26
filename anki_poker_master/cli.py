import os
import sys
import traceback
import argparse
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

from anki_poker_master.parser.phh import parse
from anki_poker_master.parser.preflop_scenario import (
    parse_scenario_yml,
    EXAMPLE_SCENARIO_FILE,
)
from anki_poker_master.model import ValidationError
from anki_poker_master.presenter.anki.phh import get_deck
from anki_poker_master.presenter.anki.preflop_scenario import create_decks
from anki_poker_master.presenter.anki import write_decks_to_file


def main():
    main_with_args(sys.argv[1:])


def main_with_args(args):
    try:
        package_version = version("anki-poker-master")
    except PackageNotFoundError:
        # package is not installed
        package_version = "dev"

    parser = argparse.ArgumentParser(
        description="AnkiPokerMaster - Create Anki decks for learning things related to Texas Hold'em Poker"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"AnkiPokerMaster {package_version}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output (e.g. for debugging purposes)",
    )

    subparsers = parser.add_subparsers()

    parser_range = subparsers.add_parser("range", help="Create decks for poker ranges")
    parser_range.set_defaults(func=_handle_range_subcommand)

    parser_range.add_argument(
        "-s", "--scenarios", type=str, help="Path to the scenarios file"
    )
    parser_range.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the resulting Anki package",
        default="./AnkiPokerMaster.apkg",
    )
    parser_range.add_argument(
        "-e",
        "--example",
        action="store_true",
        help="Write example file to the path specified by --scenarios/-s if and only if the file does not exist yet",
    )
    parser_range.add_argument(
        "-t",
        "--tag",
        dest="tags",
        metavar="TAG",
        type=str,
        action="append",
        help="Tag for the Anki decks. Can be specified multiple times.",
    )

    parser_hand = subparsers.add_parser("hand", help="Create decks for hand history")
    parser_hand.set_defaults(func=_handle_hand_subcommand)

    parser_hand.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the resulting Anki package",
        default="./AnkiPokerMaster.apkg",
    )
    parser_hand.add_argument(
        "-t",
        "--tag",
        dest="tags",
        metavar="TAG",
        type=str,
        action="append",
        help="Tag for the Anki decks. Can be specified multiple times.",
    )
    parser_hand.add_argument(
        "phh_files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="Path to one or multiple .phh files. If a directory is "
        "specified, all .phh files within that directory will be "
        "read recursively.",
    )

    args = parser.parse_args(args)
    try:
        args.func(args)
    except AttributeError:
        # func does not exist, in all likelihood because the cli was called
        # without a subcommand
        parser.print_help()
        sys.exit(1)


def _handle_range_subcommand(args):
    if args.example:
        if not args.scenarios:
            print("You need to specify --scenarios/-s to write an example file.")
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

    _create_preflop_scenario_deck(args.scenarios, tags, args.verbose, pkg_path)


def _handle_hand_subcommand(args):
    if args.output.endswith(".apkg"):
        pkg_path = args.output
    else:
        pkg_path = f"{args.output}.apkg"
    if os.path.exists(pkg_path):
        print(f"The file {pkg_path} already exists.")
        sys.exit(1)

    all_hands = []
    for f_name in args.phh_files:
        f = Path(f_name)
        if f.is_dir():
            for f2 in f.rglob("*.phh"):
                all_hands.append(parse(f2.read_text()))
        elif f.is_file():
            all_hands.append(parse(f.read_text()))

    deck, media_files = get_deck(all_hands, tags=args.tags)
    write_decks_to_file([deck], media_files, pkg_path)


def _create_preflop_scenario_deck(scenarios, tags, verbose, pkg_path):
    try:
        with open(scenarios, "r") as f:
            scenarios = parse_scenario_yml(f.read())
    except ValidationError as e:
        print(e.humanize_error())
        if verbose:
            print()
            traceback.print_exc()
        sys.exit(1)
    decks, media_files = create_decks(
        scenarios,
        tags,
    )
    write_decks_to_file(decks, media_files, pkg_path)
