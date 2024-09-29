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

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/hand_harrington-cash-10-1_q.png">
    <img
        src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/hand_harrington-cash-10-1_q.png"
        width="200"
        alt="Screenshot of the 'question' side of the resulting Anki card"
        >
</a>

Answer:

<a href="https://github.com/omarkohl/anki-poker-master/blob/main/docs/screenshots/hand_harrington-cash-10-1_q.png">
    <img
        src="https://raw.githubusercontent.com/omarkohl/anki-poker-master/refs/heads/main/docs/screenshots/hand_harrington-cash-10-1_a.png"
        width="200"
        alt="Screenshot of the 'answer' side of the resulting Anki card"
        >
</a>

## Options

### User-defined fields within the .phh file

The following are user-defined fields that can be added to the .phh file.

* **_apm_hero**: It is used to specify which player is the hero (i.e. whose
  perspective are we analyzing the game from). It can be omitted if initially
  only one player has known pocket cards, in which case it is clear that this
  player is the hero. If the pocket cards of multiple players are known then
  this option must be specified.
* **_apm_context**: It is used to add some background information at the top of
  the _question_ side of the Anki card. It's optional.
* **_apm_source**: It is used to add source information (i.e. where did you find
  this hand) to the _answer_ side of the Anki card. It is optional.
* **_apm_notes**: It is used to add some additional information to the _answer_
  side of the Anki card. It is optional.
* **_apm_answers**: It is a list of the answers to all the study spots. If it is
  specified, it must have exactly the same length as the number of study spots.
  If it is not specified then the correct answer is what was specified inline or
  the actual action by the player (see below).

### Specifying study spots within the .phh file

A study spot is a particular spot during a hand that you would like to
study/remember.

You define them by using commentaries, which are like _comments_ but contained
inside a string.

* Default is to study **every** spot that the hero has to make a decision. If
  this is what you want to do, you need to do nothing else! The correct answer
  to the question "What should you do?" for any of these spots is the action
  that the player actually took during the hand (or whatever was specified in
  the **_apm_answers** field, see above).
* If you only want to study specific spots, then mark all those spots with
  an `# apm study` commentary at the end of but within the string that defines
  the action you want to study.
* If you want to specify an answer to an `# apm study` spot inline you can do so
  by writing `# apm study: This is the correct answer` instead. Alternatively,
  you can specify answers in the **_apm_answers** field.

### Command line options

See `anki-poker-master hand --help`.

## Examples

Here are some examples to make the usage of the different options clearer.

### Unchanged .phh file

The next file is a plain .phh with no AnkiPokerMaster specific changes. It will
just work. The hero is p2 because it's the only player whose pocket cards are
known. There will be four study spots, namely `p2 cc`, `p2 cc`, `p2 cc`
and `p2 cbr 388`, that is all the spots where p2 had to make a decision. The
Anki cards will ask "What should you do?" for each of these spots, just before
the hero actually makes a decision. The answer in each of these cases will be
the actual decision that the hero made according to the hand history. Note that
this is perfectly fine assuming that the hero played correctly. Frequently,
however, you will have a hand history where the hero did one thing but later
analysis shows that another action would have been better. Continue reading for
further examples to address this.

```toml
variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 ????",
    "p3 cbr 12",
    "p1 f",
    "p2 cc",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc",
    "d db 4s",
    "p2 cc",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388",
    "p3 f",
]
```

### Modify one study spot (inline)

Let's say that we think hero should actually have folded preflop. This is how we
can specify this. Note that the rest of the hand will still play out as it did
and there are still four study spots. The only thing that has changed is that
the question to the answer "What should you do?" on the first `p2 cc` is no
longer "cc" (i.e. check) but "Fold since T8o is a weak hand."

```toml
variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 ????",
    "p3 cbr 12",
    "p1 f",
    "p2 cc # apm study: Fold since T8o is a weak hand.",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc # apm study",
    "d db 4s",
    "p2 cc # apm study",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388 # apm study",
    "p3 f",
]
```

### Modify one study spot (using _apm_answers)

The advantage of using the user-defined field **_apm_answers** is that it might
be more convenient for writing a longer text, other than that it's equivalent to
writing the answer inline.

Note that it's necessary to add one entry per study spot, even if that entry is
empty. This is to catch errors where you miscount the number of study spots and
might assign the wrong answer to the wrong spot.

Note also that it's not necessary to specify the `# apm study` commentary since
you want to study all decisions p2 made.

```toml
variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 ????",
    "p3 cbr 12",
    "p1 f",
    "p2 cc",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc",
    "d db 4s",
    "p2 cc",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388",
    "p3 f",
]

_apm_answers = [
    """Generally fold since T8o is a weak hand,
       however you should raise in 10% of cases
       for deception value.""",
    "",
    "",
    "",
]
```

### Study only some spots

Now let's assume out of the four spots you only want to study the first and the
last because the other two are obvious.

Given that we only specified two `# apm study` commentaries, there will only be
two study spots.

```toml
variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 ????",
    "p3 cbr 12",
    "p1 f",
    "p2 cc # apm study",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc",
    "d db 4s",
    "p2 cc",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388 # apm study",
    "p3 f",
]
```

### Specify the hero

In this case the pocket cards of two players are known, so we must specify whose
perspective we are taking. We do this with the user-defined field `_apm_hero`.

```toml
variant = "NT"
antes = [0, 0, 0]
blinds_or_straddles = [2, 4, 0]
min_bet = 2
starting_stacks = [110, 420, 450]
actions = [
    "d dh p1 ????",
    "d dh p2 Th8c",
    "d dh p3 KsKc",
    "p3 cbr 12",
    "p1 f",
    "p2 cc",
    "d db AhTs8h",
    "p2 cc",
    "p3 cbr 20",
    "p2 cc",
    "d db 4s",
    "p2 cc",
    "p3 cc",
    "d db Tc",
    "p2 cbr 388",
    "p3 f",
]

_apm_hero = 2
```
