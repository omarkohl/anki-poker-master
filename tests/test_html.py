import os
import textwrap
from poker.hand import Range, Hand, Rank


def compare_or_update_golden(pytestconfig, golden_file_path, actual_output):
    # If the --update-golden option was set, update the golden file
    if pytestconfig.getoption("update_golden"):
        with open(golden_file_path, "w") as file:
            file.write(actual_output)
    else:
        # Otherwise, read the golden file and compare it to the actual output
        with open(golden_file_path, "r") as file:
            golden_output = file.read()
        assert actual_output == golden_output


def test_default_extra_css(pytestconfig, golden_dir):
    """
    In the default case extra CSS should be empty since we don't need to add
    or change any colors.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    css = scenario.extra_css()
    assert css == ""


def test_custom_fold_color_css(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }
    range_colors = {
        "Fold": "yellow",
    }

    scenario = PreflopScenario(
        action_ranges, "CO", "Opening", "Cash 100BB 6P", range_colors
    )
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += scenario.html_legend()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_custom_range_css(pytestconfig, golden_dir):
    """
    Test that the custom range is added to the css with one of the predefined colors.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper
    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3s+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
        "My special range": Range("K2s+"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += scenario.html_legend()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_custom_range_with_custom_color_css(pytestconfig, golden_dir):
    """
    Test that the custom range is added to the css with the color passed in.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper
    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3s+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
        "My special range": Range("K2s+"),
    }
    range_colors = {
        "My special range": "red",
    }
    scenario = PreflopScenario(
        action_ranges, "CO", "Opening", "Cash 100BB 6P", range_colors
    )
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += scenario.html_legend()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_legend_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_legend()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_full_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_blank_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_top_left_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_top_left_quadrant_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_top_right_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_top_right_quadrant_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_bottom_left_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_bottom_left_quadrant_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_bottom_right_quadrant_blank_html(pytestconfig, golden_dir):
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_bottom_right_quadrant_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_top_right_quadrant_blank_html_with_custom_ranges(pytestconfig, golden_dir):
    """
    The purpose of this test is to verify that custom CSS also works with blank.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A3+, K3+, Q3+, J3+, T3+, 93+, 83+, 73+"),
        "Raise": Range("AA, KK, QQ, JJ, TT, 99, 88, 77"),
        "My special range": Range("K2s+"),
    }
    range_colors = {
        "My special range": "red",
    }
    scenario = PreflopScenario(
        action_ranges, "CO", "Opening", "Cash 100BB 6P", range_colors
    )
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_top_right_quadrant_blank()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_overlapping_ranges(pytestconfig, golden_dir):
    """
    Verify that overlapping ranges are overwritten in alphabetical order.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {
        "Call": Range("A8s-"),
        "AAA": Range("AKs"),
        "ZZZ": Range("AQs"),
        "Raise": Range("A4s+"),
    }

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)


def test_default_is_fold(pytestconfig, golden_dir):
    """
    Verify that if no ranges are passed in, the default is to fold.
    """
    from anki_poker_master import PreflopScenario

    from anki_poker_master import helper

    action_ranges = {}

    scenario = PreflopScenario(action_ranges, "CO", "Opening", "Cash 100BB 6P")
    html = ""
    html += (
        "<style>\n" + textwrap.indent(helper.default_css(), 4 * " ") + "\n</style>\n"
    )
    html += "<style>\n" + textwrap.indent(scenario.extra_css(), 4 * " ") + "</style>\n"
    html += scenario.html_full()
    html += "<script>\n" + textwrap.indent(helper.default_js(), 4 * " ") + "</script>\n"
    golden_html_file = os.path.join(golden_dir, "file.html")
    compare_or_update_golden(pytestconfig, golden_html_file, html)
