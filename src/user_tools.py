from pathlib import Path
import re


def read_card_counts(file_path: str | Path) -> dict[str, int]:
    """Read a UTF-8 card list and return card names mapped to total counts.

    Lines use ``3 Card Name`` format, with whitespace after the count, or just
    ``Card Name`` for a count of one. Blank lines are ignored and repeated names
    are combined (case-sensitive). Raise ValueError
    for malformed lines, nonpositive counts, or totals greater than three.
    """
    card_counts: dict[str, int] = {}
    with Path(file_path).open(encoding="utf-8-sig") as card_file:
        for line_number, line in enumerate(card_file, start=1):
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