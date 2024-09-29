# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Read poker hand histories in the .phh (Poker Hand History) format and
  convert them to Anki decks in order to study what to do in specific spots.
  The `hand` subcommand was introduced for this purpose.

### Changed

- BREAKING: The parsing of scenario.yml files was moved to the `range`
  subcommand, meaning that if you were previously
  calling `anki-poker-master -o package.apkg -s scenario.yml` you now need to
  call `anki-poker-master range -o package.apkg -s scenario.yml`.
- BREAKING: Previously it was possible to specify multiple tags separated by
  whitespace as follows `--tags poker learning 2024` whereas now it's necessary
  that `--tag` / `-t` is called with one tag every time
  i.e. `--tag poker --tag learning --tag 2024`.
- BREAKING: Require Python 3.11 or higher due to the `pokerkit` dependency.

## [0.2.0] - 2024-03-04

Initial release.

### Added

- Parse scenario.yml files that describe preflop ranges and convert them to
  Anki decks in order to memorize those ranges.

[unreleased]: https://github.com/omarkohl/anki-poker-master/compare/v0.2.0...HEAD

[1.0.0]: https://github.com/omarkohl/anki-poker-master/compare/v0.2.0...v1.0.0

[0.2.0]: https://github.com/omarkohl/anki-poker-master/releases/tag/v0.2.0
