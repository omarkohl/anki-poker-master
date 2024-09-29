# Decisions

Document some (design) decisions for future reference.

## Study hand history

**UPDATE:** This will be implemented for version 1.0.0 .

Allow studying a specific spot. For example NL $1/$2 6-max cash game. All players
are tight. All players have 100BB. You are in the SB with 6s6h. LJ raises to $6,
everyone else folds, you call, BB folds. The flop is Kh4s7s. What do you do?

The hand itself should be documented in a more or less standard textual format,
for example:

* Poker Stars textual format:
    * Positive: It's a popular format. At least one GUI
      [tool](https://livesqueezer.winningpokerhud.com/) exists to create such
      files.
    * Negative: Does not seem to be formally specified anywhere. There seems to
      be no working parser ("poker" library seems to be having
      [issues](https://github.com/pokerregion/poker/issues/37)).
* OHH (Open Hand History):
    * Positive: Has a [specification](https://hh-specs.handhistory.org/).
    * Negative: Uses JSON, which is not so nice to read and write by hand.
    * Negative: There seems to be no tool or library that can parse it.
* PHH (Poker Hand History):
    * Positive: Very thoroughly
      [specified](https://arxiv.org/html/2312.11753v2) plus a
      [parser implementation](https://github.com/uoftcprg/pokerkit).
    * Positive: Uses the TOML format, which is humanly writable and
      tool-friendly.
    * Negative: There seems to be no tooling to create such a file (e.g. with a
      graphical interface).
    * Positive: Supports user-defined fields which might be suitable to include
      Anki answers to the spots being analyzed (otherwise they would need to be
      stored in a separate file).

PHH seems to be the best alternative.

Some informal requirements:

* Per hand, it must be possible to study multiple spots (e.g. what to do after
  the first villain raise preflop, what to do when first to act on the river,
  etc.).
* It must be possible NOT to study trivial spots (i.e. don't automatically
  generate Anki cards for every action that Hero needs to take).
* The display format of the hand history must be suitable for fast and easy
  study also on the phone.

Assuming the PHH format it would be possible to include a commentary to the
actions after which you want to study the decision. Using used-defined fields
the answers to those spots could be specified. If no answer is specified instead
the very next action could be the automatic answer (assuming that the hand
history represents the ideal choice in every case). It would also be possible to
default to create an Anki card for every decision that Hero needs to make if
nothing else is specified. This would allow using a completely standard PHH file
without any modifications.

The Hero player could be determined either automatically as the only player
where the pocket cards are known or with a used-defined field.

Maybe it would be nice to support studying without knowing your own cards (i.e.
only by considering your own range). I'm not sure how useful that is, and I'll
skip it in the beginning in the spirit of KISS.

It's probably desirable to keep the PHH parsing code decoupled from the rest in
order to support other formats in the future.
