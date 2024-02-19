from poker.hand import Range, Hand, Rank
from typing import Dict
from anki_poker_generator import PreflopScenario
from anki_poker_generator.anki import create_deck, write_deck_to_file


def main():
    config = {}
    source = "https://pokertrainer.se/"
    scenarios = []
    scenarios.append(PreflopScenario(
        {
            "Raise": Range('A2s+, K5s+, Q9s+, JTs, T9s, ATo+, KJo+, QJo+, 77+'),
        },
        "LJ",
        "Opening",
        "Cash 100BB 6P",
        config,
        source,
        ))
    scenarios.append(PreflopScenario(
        {
            "Raise": Range('A2s+, K5s+, Q8s+, J9s+, T9s, A9o+, KTo+, QTo+, 66+'),
        },
        "HJ",
        "Opening",
        "Cash 100BB 6P",
        config,
        source,
        ))
    d = create_deck(scenarios)
    write_deck_to_file(d, "preflop.apkg")


if __name__ == '__main__':
    main()
