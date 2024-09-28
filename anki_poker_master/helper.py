import re
from numbers import Number

from importlib_resources import files


def default_css():
    return files("anki_poker_master").joinpath("resources", "default.css").read_text()


def default_js():
    return files("anki_poker_master").joinpath("resources", "default.js").read_text()


def blank_table():
    return (
        files("anki_poker_master").joinpath("resources", "blank_table.html").read_text()
    )


def str_to_css_class(action: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", action).lstrip("_").lower().strip()


def format_n(n: Number) -> str:
    """
    Return the number as a string with thin space as separator.
    """
    return f'{n:,}'.replace(',', u'\u2009')
