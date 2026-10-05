from pathlib import Path
import re

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


def read_card_counts(text: list[str]) -> dict[str, int]:
    """Read a UTF-8 card list and return card names mapped to total counts.

    Lines use ``3 Card Name`` format, with whitespace after the count, or just
    ``Card Name`` for a count of one. Blank lines are ignored and repeated names
    are combined (case-sensitive). Raise ValueError
    for malformed lines, nonpositive counts, or totals greater than three.
    """
    card_counts: dict[str, int] = {}
    for line_number, line in enumerate(text, start=1):
        line = line.strip()
        if not line:
            continue

        match = re.fullmatch(r"([+-]?[0-9]+)\s+(.+)", line)
        if match is not None:
            count = int(match.group(1))
            name = match.group(2).strip()
        elif re.fullmatch(r"[+-]?[0-9]+", line):
            raise ValueError(
                f"Line {line_number}: missing card name after count."
            )
        else:
            count = 1
            name = line

        if count < 1:
            raise ValueError(f"Line {line_number}: count must be positive.")

        total = card_counts.get(name, 0) + count
        if total > 3:
            raise ValueError(
                f"Line {line_number}: {name!r} has a total count of {total}; "
                "the maximum is 3."
            )
        card_counts[name] = total

    return card_counts

if __name__ == "__main__":
    test_file = Path(__file__).resolve().parent.parent / "testing" / "mantis.txt"
    result = read_card_counts(test_file)
    print(result)