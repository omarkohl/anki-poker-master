from importlib_resources import files


def default_css():
    return files("anki_poker_master").joinpath("resources", "default.css").read_text()
