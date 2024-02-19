from poker.hand import Range, Hand, Rank
from typing import Dict
from anki_poker_generator import PreflopScenario
from anki_poker_generator.anki import create_deck, write_deck_to_file


def main():
    action_ranges = {
        "Raise": Range('A2s+, K5s+, Q9s+, JTs, T9s, ATo+, KJo+, QJo+, 77+'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "LJ", "Opening", "Cash 100BB 6P", config)
    d = create_deck(scenario)
    write_deck_to_file(d, "preflop.apkg")


if __name__ == '__main__':
    main()
