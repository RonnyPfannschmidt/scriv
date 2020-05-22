"""Test collection logic."""

ENTRY1 = """\
Fixed
-----

- Launching missiles no longer targets ourselves.
"""

ENTRY2 = """\
Added
-----

- Now you can send email with this tool.

Fixed
-----

- Typos corrected.
"""

ENTRY3 = """\
Obsolete
--------

- This section has the wrong name.
"""

CHANGELOG_1_2 = """\

Added
-----

- Now you can send email with this tool.

Fixed
-----

- Launching missiles no longer targets ourselves.

- Typos corrected.
"""

CHANGELOG_2_1_3 = """\

Added
-----

- Now you can send email with this tool.

Fixed
-----

- Typos corrected.

- Launching missiles no longer targets ourselves.

Obsolete
--------

- This section has the wrong name.
"""

MARKED_CHANGELOG_A = """\
================
My Great Project
================

Blah blah.

Changes
=======

.. scriv:insert-here
"""

UNMARKED_CHANGELOG_B = """\

Other stuff
===========

Blah blah.
"""


def test_collect_simple(cli_invoke, changelog_d, temp_dir):
    # Sections are ordered by the config file.
    # Entries in sections are in time order.
    (changelog_d / "scriv.ini").write_text("# this shouldn't be collected\n")
    (changelog_d / "20170616_nedbat.rst").write_text(ENTRY1)
    (changelog_d / "20170617_nedbat.rst").write_text(ENTRY2)
    cli_invoke(["collect"])
    changelog_text = (temp_dir / "CHANGELOG.rst").read_text()
    assert CHANGELOG_1_2 == changelog_text
    # We didn't use --delete, so the files should still exist.
    assert (changelog_d / "scriv.ini").exists()
    assert (changelog_d / "20170616_nedbat.rst").exists()
    assert (changelog_d / "20170617_nedbat.rst").exists()


def test_collect_ordering(cli_invoke, changelog_d, temp_dir):
    # Entries in sections are in time order.
    # Unknown sections come after the known ones.
    (changelog_d / "20170616_nedbat.rst").write_text(ENTRY2)
    (changelog_d / "20170617_nedbat.rst").write_text(ENTRY1)
    (changelog_d / "20170618_joedev.rst").write_text(ENTRY3)
    cli_invoke(["collect"])
    changelog_text = (temp_dir / "CHANGELOG.rst").read_text()
    assert CHANGELOG_2_1_3 == changelog_text


def test_collect_inserts_at_marker(cli_invoke, changelog_d, temp_dir):
    # Collected text is inserted into CHANGELOG where marked.
    changelog = temp_dir / "CHANGELOG.rst"
    changelog.write_text(MARKED_CHANGELOG_A + UNMARKED_CHANGELOG_B)
    (changelog_d / "20170617_nedbat.rst").write_text(ENTRY1)
    cli_invoke(["collect"])
    changelog_text = changelog.read_text()
    expected = MARKED_CHANGELOG_A + "\n" + ENTRY1 + UNMARKED_CHANGELOG_B
    assert expected == changelog_text


def test_collect_prepends_if_no_marker(cli_invoke, changelog_d, temp_dir):
    # Collected text is inserted at the top of CHANGELOG if no marker.
    changelog = temp_dir / "CHANGELOG.rst"
    changelog.write_text(UNMARKED_CHANGELOG_B)
    (changelog_d / "20170617_nedbat.rst").write_text(ENTRY1)
    cli_invoke(["collect"])
    changelog_text = changelog.read_text()
    expected = "\n" + ENTRY1 + UNMARKED_CHANGELOG_B
    assert expected == changelog_text


def test_collect_and_delete(cli_invoke, changelog_d, temp_dir):
    (changelog_d / "scriv.ini").write_text("# this shouldn't be collected\n")
    (changelog_d / "20170616_nedbat.rst").write_text(ENTRY1)
    (changelog_d / "20170617_nedbat.rst").write_text(ENTRY2)
    cli_invoke(["collect", "--delete"])
    changelog_text = (temp_dir / "CHANGELOG.rst").read_text()
    assert CHANGELOG_1_2 == changelog_text
    # We used --delete, so the collected files should be gone.
    assert (changelog_d / "scriv.ini").exists()
    assert not (changelog_d / "20170616_nedbat.rst").exists()
    assert not (changelog_d / "20170617_nedbat.rst").exists()