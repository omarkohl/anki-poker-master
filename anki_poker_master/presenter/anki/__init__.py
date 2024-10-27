from typing import List, Set

import genanki
from importlib_resources import files

from anki_poker_master import helper

_BASIC_HEADER = """
<div class="row">
    <div class="column column_left">
        {{Tags}}
    </div>
    <div class="column column_right">
    </div>
</div>
""".lstrip()

_BASIC_FOOTER = """
{{#Notes}}
<p>
<small><b>Notes:</b></small>
<br>
<small>{{Notes}}</small>
</p>
{{/Notes}}
{{#Source}}
<p>
<small><b>Source:</b></small>
<br>
<small>{{Source}}</small>
</p>
{{/Source}}
""".lstrip()

BASIC_MODEL = genanki.Model(
    1708087674509,
    "APM Basic",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "Notes", "size": 14},
        {"name": "Source", "size": 14},
    ],
    templates=[
        {
            "name": "QA",
            "qfmt": _BASIC_HEADER + "{{Question}}",
            "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}<br>" + _BASIC_FOOTER,
            "bqfmt": "{{Question}}",
            "bafmt": "{{Answer}}",
        },
    ],
    css=helper.default_css(),
)


# The maximum number of QA pairs that can be added to the hand history model.
HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS = 20


def _get_hand_history_model_qa_template(qa_index: int) -> dict:
    """
    Return a QA template for the hand history model with the
    given index.
    This is a helper function for the HAND_HISTORY_MODEL to avoid
    repeating the same template definition many times.
    """
    # Note that Anki templates use double curly braces for the fields and when
    # using Python format strings we need to escape them by doubling them.
    return {
        "name": f"QA{qa_index}",
        "qfmt": (
            f"{{{{#Q{qa_index}}}}}\n"
            + _BASIC_HEADER
            + "\n"
            + '<div class="hand-history">\n'
            + "<h1>{{Title}}</h1>\n"
            + "{{#Context}}\n"
            + "<p>{{Context}}</p>\n"
            + "{{/Context}}\n"
            + '<div class="pocket-cards">\n'
            + "{{Hero Cards}}\n"
            + "</div>\n"
            + "<p><strong>Hero:</strong> {{Hero}}</p>\n"
            + f"{{{{Q{qa_index}}}}}\n"
            + "</div>\n"
            + f"{{{{/Q{qa_index}}}}}"
        ),
        "afmt": (
            f"{{{{FrontSide}}}}"
            f"<hr id='answer'>{{{{A{qa_index}}}}}<br>"
            f"{_BASIC_FOOTER}"
        ),
        "bqfmt": f"{{{{Q{qa_index}}}}}",
        "bafmt": f"{{{{A{qa_index}}}}}",
    }


def _get_hand_history_qa_fields(qa_index: int) -> List[dict]:
    """
    Return a list of fields for the hand history model with the
    given index.
    This is a helper function for the HAND_HISTORY_MODEL to avoid
    repeating the same field definition many times.
    """
    return [
        {"name": f"Q{qa_index}", "collapsed": True},
        {"name": f"A{qa_index}", "collapsed": True},
    ]


HAND_HISTORY_MODEL = genanki.Model(
    1771292474,  # Random number that should not change
    "APM Hand History",
    fields=[
        {"name": "Title"},
        {"name": "Context"},
        {"name": "Hero Cards"},
        {"name": "Hero"},
        *sum(
            [
                _get_hand_history_qa_fields(i)
                for i in range(1, HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS + 1)
            ],
            [],
        ),
        {"name": "Notes", "size": 14},
        {"name": "Source", "size": 14},
    ],
    templates=[
        *[
            _get_hand_history_model_qa_template(i)
            for i in range(1, HAND_HISTORY_MODEL_MAX_NUM_QUESTIONS + 1)
        ],
    ],
    css=helper.default_css(),
)


def write_decks_to_file(
    decks: List[genanki.Deck], media_files: Set[str], filename: str
):
    media_files_full_path = []
    for media_file in media_files:
        image_path = files("anki_poker_master").joinpath(
            "resources", "images", media_file
        )
        media_files_full_path.append(image_path)
    genanki.Package(decks, media_files_full_path).write_to_file(filename)
