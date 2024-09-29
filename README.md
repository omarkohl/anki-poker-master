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

See the [usage documentation](docs/usage) for more information (and
screenshots).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Develop

Do you want to contribute to this project? See [docs/dev](docs/dev).

## Support / Help

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
