import os
from poker.hand import Range, Hand, Rank


def compare_or_update_golden(pytestconfig, golden_file_path, actual_output):
    # If the --update-golden option was set, update the golden file
    if pytestconfig.getoption("update_golden"):
        with open(golden_file_path, 'w') as file:
            file.write(actual_output)
    else:
        # Otherwise, read the golden file and compare it to the actual output
        with open(golden_file_path, 'r') as file:
            golden_output = file.read()
        assert actual_output == golden_output


def test_default_css(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    css = scenario.css()

    golden_css_file = os.path.join(golden_dir, "file.css")
    compare_or_update_golden(pytestconfig, golden_css_file, css)


def test_custom_fold_color_css(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {
        "color": {
            "Fold": "yellow",
        }
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    css = scenario.css()
    golden_css_file = os.path.join(golden_dir, "file.css")
    compare_or_update_golden(pytestconfig, golden_css_file, css)


def test_custom_range_css(pytestconfig, golden_dir):
    """
    Test that the custom range is added to the css with one of the predefined colors.
    """
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3s+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
        "My special range": Range('K2s+'),
    }
    config = {}
    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    css = scenario.css()
    golden_css_file = os.path.join(golden_dir, "file.css")
    compare_or_update_golden(pytestconfig, golden_css_file, css)


def test_custom_range_with_custom_color_css(pytestconfig, golden_dir):
    """
    Test that the custom range is added to the css with the color passed in.
    """
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3s+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
        "My special range": Range('K2s+'),
    }
    config = {
        "color": {
            "My special range": "red",
        }
    }
    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    css = scenario.css()
    golden_css_file = os.path.join(golden_dir, "file.css")
    compare_or_update_golden(pytestconfig, golden_css_file, css)


def test_legend_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_legend()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_full_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_full()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_blank_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_blank()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_top_left_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_top_left_quadrant_blank()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_top_right_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_top_right_quadrant_blank()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_bottom_left_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_bottom_left_quadrant_blank()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_bottom_right_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_bottom_right_quadrant_blank()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_header_html(pytestconfig, golden_dir):
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+'),
        "Raise": Range('AA, KK, QQ, JJ, TT, 99, 88, 77'),
    }
    config = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.header()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)

def test_overlapping_ranges(pytestconfig, golden_dir):
    """
    Verify that overlapping ranges are overwritten in alphabetical order.
    """
    from anki_poker_generator import PreflopScenario
    action_ranges = {
        "Call": Range('A8s-'),
        "AAA": Range('AKs'),
        "ZZZ": Range('AQs'),
        "Raise": Range('A4s+'),
    }
    config = {}
    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_full()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)

def test_default_is_fold(pytestconfig, golden_dir):
    """
    Verify that if no ranges are passed in, the default is to fold.
    """
    from anki_poker_generator import PreflopScenario
    action_ranges = {}
    config = {}
    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P", config)
    html = scenario.css() + scenario.html_full()
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)