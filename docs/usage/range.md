# Study Preflop Ranges

Learn/memorize which hands to fold, raise or call with preflop.

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

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/k3_q.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/k3_q.jpg" width="200">
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/k3_a.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/k3_a.jpg" width="200">
</a>

When opening as Lojack, how should you play Jack and another suited card?

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/jx_q.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/jx_q.jpg" width="200">
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/jx_a.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/jx_a.jpg" width="200">
</a>

What table position does the following range table correspond to? (this question
is a memorization aid)

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/position_q.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/position_q.jpg" width="200">
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/position_a.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/position_a.jpg" width="200">
</a>

Fill in the blank cells in this range table.

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/quadrant_q.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/quadrant_q.jpg" width="200">
</a>

Note that here it's possible to mark cells using the mouse or finger
(touchscreen) as a memory aid before flipping to the answer side.

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/quadrant_q_marking.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/quadrant_q_marking.jpg" width="200">
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/quadrant_a.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/quadrant_a.jpg" width="200">
</a>


Of course also with dark mode: How should you open with QQ as Hijack?

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/qq_q.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/qq_q.jpg" width="200">
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/qq_a.jpg">
    <img src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/qq_a.jpg" width="200">
</a>
