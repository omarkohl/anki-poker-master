def compare_or_update_golden(pytestconfig, golden_file_path, actual_output):
    """
    If the --update-golden command line option is present then update the golden file with the
    actual_output, otherwise assert that the content of the file is equal to the actual output.
    """
    # Tell pytest to not show this function but its caller when displaying a failed test
    __tracebackhide__ = True

    # If the --update-golden option was set, update the golden file
    if pytestconfig.getoption("update_golden"):
        with open(golden_file_path, "w") as file:
            file.write(actual_output)
    else:
        # Otherwise, read the golden file and compare it to the actual output
        with open(golden_file_path, "r") as file:
            golden_output = file.read()
        assert actual_output == golden_output
