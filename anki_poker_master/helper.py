from importlib_resources import files


def default_css():
    return files("anki_poker_master").joinpath("resources", "default.css").read_text()


def default_js():
    return files("anki_poker_master").joinpath("resources", "default.js").read_text()


def blank_table():
    return (
        files("anki_poker_master").joinpath("resources", "blank_table.html").read_text()
    )
