from poker.hand import Range, Hand, Rank
from typing import Dict
from anki_poker_generator import PreflopScenario
from anki_poker_generator.anki import create_deck, write_deck_to_file


def main():
    config = {}
    source = '<a href="https://pokertrainer.se/">pokertrainer.se</a>'
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
    scenarios.append(PreflopScenario(
        {
            "Raise": Range('A2s+, K3s+, Q5s+, J7s+, T8s+, 98s+, A8o+, K9o+, QTo+, JTo+, 22+'),
        },
        "CO",
        "Opening",
        "Cash 100BB 6P",
        config,
        source,
        ))
    scenarios.append(PreflopScenario(
        {
            "Raise": Range('A2s+, K2s+, Q2s+, J4s+, T6s+, 96s+, 86s+, 75s+, 65s+, 54s+, A3o+, K8o+, Q9o+, J9o+, T9o+, 22+'),
        },
        "BTN",
        "Opening",
        "Cash 100BB 6P",
        config,
        source,
        "Same range as SB."
        ))
    scenarios.append(PreflopScenario(
        {
            "Raise": Range('A2s+, K2s+, Q2s+, J4s+, T6s+, 96s+, 86s+, 75s+, 65s+, 54s+, A3o+, K8o+, Q9o+, J9o+, T9o+, 22+'),
        },
        "SB",
        "Opening",
        "Cash 100BB 6P",
        config,
        source,
        "Same range as BTN."
        ))
    d = create_deck(scenarios)
    write_deck_to_file(d, "preflop.apkg")


if __name__ == '__main__':
    main()
