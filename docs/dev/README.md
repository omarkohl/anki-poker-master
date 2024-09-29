# Development documentation

Check the repository on GitHub: https://github.com/omarkohl/anki-poker-master

```bash
poetry install
poetry run anki-poker-master
# poetry shell
```

You might also be interested in:

* Future [ideas](ideas.md) for this project.
* Past [design decisions](decisions.md).

## Tests

```bash
poetry run pytest
```

Most of the tests generate output that is compared with golden files (i.e.
files containing the expected output). This has the big advantage that you can
look at these files easily to see what the functions actually generate. Looking
at the HTML files in a browser gives you the full experience.

If you modify the code instead of having to manually fix all golden files you
can run the following command to overwrite them all. Obviously you should only
do this if you understand what you are changing.

```bash
poetry run pytest --update-golden
```

Occasionally you should delete all golden files and re-generate them to make
sure there are no orphaned files lying around because a test was renamed or
deleted:

```bash
rm -rf tests/golden
poetry run pytest --update-golden
```

### Manual tests

Currently, some tests are not automated because they would require
programmatically
evaluating Anki decks. For now doing it manually is simpler. The tests will
interactively guide you.

```bash
APM_MANUAL_TESTS=true poetry run pytest tests/test_manual.py -s
```
