# AnkiPokerMaster

Python tool to generate one or multiple Anki decks for learning things related
to Texas Hold'em
Poker, for example preflop ranges or the correct action to take in specific
spots in a hand.

Anki is a powerful tool to learn and memorize useful information. It is
available for Windows, Linux, macOS, Android and iOS. [Official
website](https://apps.ankiweb.net/) and [inspiring
examples](https://augmentingcognition.com/ltm.html) of the power of Anki.

You can read some more about Poker preflop ranges
[here](https://www.splitsuit.com/poker-ranges-reading) and
[here](https://pokertrainer.se/preflop-introduction/).

Hands that you might want to study must be documented in the .phh format. You
can read the specification for that
format: [Poker Hand History File Format Specification](https://arxiv.org/html/2312.11753v2).
Or just check the examples below.

<a href="https://pypi.org/project/anki_poker_master/">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/anki_poker_master">
</a>

## Usage

Install using pip:

```bash
pip install anki_poker_master
```

Execute the command to see help:

```bash
anki-poker-master -h
```

### Preflop ranges

Write a YAML file to define all scenarios (situations) you want to memorize,
for example "Opening as Button in a 100BB Cash game". AnkiPokerMaster will
generate Anki decks based solely on this scenario.yml file and you will get
Anki cards like the screenshots below.

```yaml
- game: "Cash 100BB 6P"
  position: "LJ"
  scenario: "Opening"
  ranges:
    Raise: "A2s+, K5s+, Q9s+, JTs, T9s, ATo+, KJo+, QJo+, 77+"
  source: pokertrainer.se
```

See a more complex example here:
[example_scenarios.yml](https://github.com/omarkohl/anki-poker-master/blob/main/example_scenarios.yml)

```bash
anki-poker-master range -s scenarios.yml -o Poker.apkg
```

`Poker.apkg` is a regular Anki package file and can be imported into Anki.

Execute `anki-poker-master --help` to see more usage information.

#### Ranges

Some examples for how ranges can be specified:

* **77+** (All pairs 77 and up i.e. 77, 88, 99, ...)
* **77-** (All pairs 77 and below i.e. 77, 66, 55, ...)
* **A2s+** (A2 suited and up excluding pairs i.e. A2s, A3s, A4s, ...)
* **KT+** (KT and up both suited and offsuit excluding pairs i.e. KTs, KJs, KQs,
  KTo, KJo and KQo)
* **23s** (A specific hand i.e. 23s)
* **95s-98s** (Hands between i.e. 95s, 96s, 97s and 98s)
* Combining any of the above separated by commas

#### Screenshots

When opening as the small blind, how should you play King Three offsuit?

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/k3_q.jpg?raw=true" width="200">

Answer:

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/k3_a.jpg?raw=true" width="200">

When opening as Lojack, how should you play Jack and another suited card?

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/jx_q.jpg?raw=true" width="200">

Answer:

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/jx_a.jpg?raw=true" width="200">

What table position does the following range table correspond to? (this question
is a memorization aid)

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/position_q.jpg?raw=true" width="200">

Answer:

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/position_a.jpg?raw=true" width="200">

Fill in the blank cells in this range table.

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/quadrant_q.jpg?raw=true" width="200">

Note that here it's possible to mark cells using the mouse or finger
(touchscreen) as a memory aid before flipping to the answer side.

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/quadrant_q_marking.jpg?raw=true" width="200">

Answer:

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/quadrant_a.jpg?raw=true" width="200">


Of course also with dark mode: How should you open with QQ as Hijack?

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/qq_q.jpg?raw=true" width="200">

Answer:

<img src="https://github.com/omarkohl/anki-poker-master/blob/main/screenshots/qq_a.jpg?raw=true" width="200">

### Hand history

If you want to study what the correction action is in particular spot during a
hand, this is what you are looking for.

Create a .phh file that documents the hand you are interested in. The file must
follow
the [Poker Hand History File Format Specification](https://arxiv.org/html/2312.11753v2),
which among other things means it must be valid [TOML](https://toml.io/). In
addition, there are some optional user-defined fields specific to
AnkiPokerMaster, namely `_apm_hero`, `_apm_context`, `_apm_source`
and `_apm_answers`. The spots you want to study _can_ be marked using
the `# apm study` commentary (otherwise it will default to studying every spot
where the hero has to make a decision). See the examples to get a better
understanding.

`harrington-cash-10-1.phh`

```toml
variant = 'NT'
ante_trimming_status = true
antes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
blinds_or_straddles = [1, 2, 0, 0, 0, 0, 0, 0, 0, 0]
min_bet = 2

# All starting stacks are unknown excepts the ones marked
starting_stacks = [
    200,
    200,
    200,
    200,
    200,
    200,
    300, # known
    250, # known approximately
    200,
    100, # known
]

actions = [
    'd dh p1 ????',
    'd dh p2 ????',
    'd dh p3 ????',
    'd dh p4 ????',
    'd dh p5 ????',
    'd dh p6 ????',
    'd dh p7 TcTd',
    'd dh p8 ????',
    'd dh p9 ????',
    'd dh p10 ????',
    'p3 f',
    'p4 f',
    'p5 f',
    'p6 f',
    'p7 cbr 15',
    'p8 cc',
    'p9 f',
    'p10 cbr 100',
    'p1 f',
    'p2 f',
    'p7 cbr 300 # apm study',
    'p8 f',
    'p7 sm TcTd',
    'p10 sm 2s2h', # the suits are unknown
    'd db KdQc7h',
    'd db 7d',
    'd db 4s',
]

currency = "USD"

_apm_hero = 7

_apm_context = """Major Las Vegas casino. You are up 50 BB. The BTN just sat
down, middle aged guy with a lot of jewelry that had a drink or two recently.
The player behind you hasn't been very active."""

_apm_source = """Part 10 - Beating Weak Games<br>
Harrington on Cash Games - Volume II<br>
Dan Harrington and Bill Robertie<br>
March 2008"""

_apm_answers = [
    """Go all in. He might have a big hand, but usually not. For him Poker is
    about balls. You should worry a little about the opponent behind you, but
    he is unlikely to be able to call two all-ins.""",
]
```

Execute the following command to create an Anki deck based on the above .phh
file:

```bash
anki-poker-master hand --tag poker -o Poker.apkg harrington-cash-10-1.phh
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Develop

Check the repository on GitHub: https://github.com/omarkohl/anki-poker-master

```bash
poetry install
poetry run anki-poker-master
# poetry shell
```

See the [docs/](docs/) directory for some additional documentation.

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

Occasionally you should delete all golden files and re-generate them to make
sure there are no orphaned files lying around because a test was renamed or
deleted:

```bash
rm -rf tests/golden
poetry run pytest --update-golden
```

### Manual tests

Currently some tests are not automated because they would require
programatically
evaluating Anki decks. For now doing it manually is simpler. The tests will
interactively guide you.

```bash
APM_MANUAL_TESTS=true poetry run pytest tests/test_manual.py -s
```

## Support

Raise any issues
on [GitHub](https://github.com/omarkohl/anki-poker-master/issues/new/choose).

## License

Unless otherwise specified, the code is under
the [MIT license](https://github.com/omarkohl/anki-poker-master/blob/main/LICENSE)
and
the card images are published under
[LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.html.en) (see below for
original
source of the card images).

## Credits

### Playing Cards

Slightly modified (see list of changes in
[playing-cards.svg](https://github.com/omarkohl/anki-poker-master/blob/main/playing-cards.svg))
from original source:

Vector Playing Cards 3.2  
https://totalnonsense.com/open-source-vector-playing-cards/  
Copyright 2011,2021 – Chris Aguilar – conjurenation@gmail.com  
Licensed under: LGPL 3.0 - https://www.gnu.org/licenses/lgpl-3.0.html

### Inspiration

* https://github.com/TheJakeSchmidt/anki-poker-generator
* https://pokercoaching.com/range-analyzer/
