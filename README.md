# AnkiPokerMaster

Python tool to generate one or multiple Anki decks for memorizing Texas Hold'em
Poker preflop ranges.


## Develop

```bash
poetry install
poetry run anki-poker-master
# poetry shell
```

## Tests

```bash
poetry run pytest
```

Most of the tests generate output that is compared with golden files (i.e.
files containing the expected output). This has the big advantage that you can
look at these files easily to see what the functions actually generate. Looking
at the HTML files in a browser gives you the full experience.

If you modify the code instead of having to manually fix all golden files you
can run the following command to overwrite them all. Obviously you should only
do this if you understand what you are changing.

```bash
poetry run pytest --update-golden
```

### Manual tests

Currently some tests are not automated because they would require programatically
evaluating Anki decks. For now doing it manually is simpler. The tests will
interactively guide you.

```bash
APM_MANUAL_TESTS=true poetry run pytest tests/test_manual.py -s
```

## Credits

### Playing Cards

Slightly modified from original source:

Vector Playing Cards 3.2
https://totalnonsense.com/open-source-vector-playing-cards/
Copyright 2011,2021 – Chris Aguilar – conjurenation@gmail.com
Licensed under: LGPL 3.0 - https://www.gnu.org/licenses/lgpl-3.0.html
