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
