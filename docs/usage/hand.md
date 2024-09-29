# Study Hand Histories

Learn/memorize what to do during any spot in a hand (e.g. after
the villain raised on the river with a specific board etc.).

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

The result will be an Anki deck containing one (because there was only one study
spot) Anki card:

Question:

<img
    src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/hand_harrington-cash-10-1_q.png"
    width="200"
    alt="Screenshot of the 'question' side of the resulting Anki card"
    >

Answer:

<img
    src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/hand_harrington-cash-10-1_a.png"
    width="200"
    alt="Screenshot of the 'answer' side of the resulting Anki card"
    >
