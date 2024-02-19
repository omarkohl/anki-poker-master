from poker.hand import Range, Hand, Rank
from typing import Dict
from anki_poker_generator import PreflopScenario


def main():
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
        "Something special": Range('AKs'),
        "Something special 2": Range('AQs'),
        "Something special 3": Range('AJs'),
        "Something special 4": Range('ATs'),
        "Something special 5": Range('KQs'),
        "Something special 6": Range('KJs'),
        "Something special 7": Range('KTs'),
        "Something special 8": Range('QJs'),
        "Something special 9": Range('QTs'),
        "Something special 10": Range('JTs'),
        "Something special 11": Range('AKo'),
        "Something special 12": Range('AQo'),
    }
    config = {
        "color": {
            "Fold": "yellow",
        }
    }

    scenario = PreflopScenario(action_ranges, "UTG", "3bet", "NLHE", config)
    html = ""
    html += scenario.css()
    html += scenario.header()
    html += scenario.html_blank()
    html += scenario.html_full()
    html += scenario.html_top_left_quadrant_blank()
    html += scenario.html_top_right_quadrant_blank()
    html += scenario.html_bottom_left_quadrant_blank()
    html += scenario.html_bottom_right_quadrant_blank()
    html += scenario.html_legend()
    with open("index.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    main()
