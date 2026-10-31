from pathlib import Path
import re

import utils

def store_text_file_as_list(file_path: str | Path) -> list[str]:
    """Read a UTF-8 text file and return a list of non-empty lines.

    Lines are stripped of leading and trailing whitespace. Blank lines are ignored.
    """
    lines: list[str] = []
    with Path(file_path).open(encoding="utf-8-sig") as text_file:
        for line_number, line in enumerate(text_file, start=1):
            stripped_line = line.strip()
            if stripped_line:
                lines.append(stripped_line)
    return lines


def read_card_counts(text: list[str], text_ctrl_object=None) -> dict[str, int] | None:
    """Read a UTF-8 card list and return card names mapped to total counts.

    Lines use ``3 Card Name`` format, with whitespace after the count, or just
    ``Card Name`` for a count of one. Blank lines are ignored and repeated names
    are combined (case-sensitive). Raise ValueError
    for malformed lines, nonpositive counts, or totals greater than three.
    """
    card_counts: dict[str, int] = {}
    valid = True
    for line_number, line in enumerate(text, start=1):
        line = line.strip()
        if not line:
            continue

        match = re.fullmatch(r"([+-]?[0-9]+)\s+(.+)", line)
        if match is not None:
            count = int(match.group(1))
            name = match.group(2).strip()
        elif re.fullmatch(r"[+-]?[0-9]+", line):
            valid = False
            utils.message(text_ctrl_object,f"Line {line_number}: missing card name after count.")
            utils.message(text_ctrl_object,f"Line was: {line}")
        else:
            count = 1
            name = line

        if count < 1:
            valid = False
            utils.message(text_ctrl_object,f"Line {line_number}: count must be positive.")
            utils.message(text_ctrl_object,f"Line was: {line}")

        total = card_counts.get(name, 0) + count
        card_counts[name] = total

    if valid:
        return card_counts
    return None
