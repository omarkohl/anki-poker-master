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
