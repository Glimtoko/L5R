from pathlib import Path
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from db_tools import find_card
from user_tools import read_card_counts, store_text_file_as_list


def load_cards(file_contents: list) -> dict[str, dict] | None:
    """Read card counts and look up every card in the database.

    Map each card name to its count and the (table name, details) returned by
    find_card. Print an error for each missing card and return None if any are
    missing. File-reading and card-count validation errors propagate normally.
    """
    # file_contents = store_text_file_as_list(file_path)
    card_counts = read_card_counts(file_contents)
    cards: dict[str, dict] = {}
    has_errors = False

    for name, count in card_counts.items():
        card_data = find_card(name)
        if card_data is None:
            print(f"Error: card {name!r} was not found in the database.")
            has_errors = True
            continue

        cards[name] = {"count": count, "data": card_data}

    return None if has_errors else cards


def create_proxy_pdf(cards: dict[str, dict], output_path: str | Path, custom_gap: int = 1) -> Path | None:
    """Create an A4 PDF beside the input file and return its path.

    Use nine 63 x 88 mm slots per page with <custom_gap> mm gaps between slots,
    preserving image aspect ratios.
    Database image paths are relative to the project root (the parent of src).
    Use the first available image when a card has multiple editions. Report
    missing/unreadable images and return None before creating a PDF if any
    card cannot be printed. An empty card list also returns None.
    """
    # cards = load_cards(file_path)
    if cards is None:
        return None
    if not cards:
        print("Error: the card list is empty.")
        return None

    project_root = Path(__file__).resolve().parent.parent
    images = []
    has_errors = False
    for name, card in cards.items():
        _, details = card["data"]
        try:
            image_entries = json.loads(details.get("image") or "[]")
            image_paths = [
                project_root / entry["text"] for entry in image_entries
            ]
            image_path = next(path for path in image_paths if path.is_file())
            image = ImageReader(str(image_path))
            image.getRGBData()  # Validate the image before opening the output.
        except (ValueError, TypeError, KeyError, StopIteration, OSError) as error:
            print(f"Error: no usable image for card {name!r}: {error}")
            has_errors = True
            continue
        images.append((name, image, card["count"]))

    if has_errors:
        return None

    page_width, page_height = A4
    card_width, card_height = 63 * mm, 88 * mm
    gap = custom_gap * mm
    columns = int((page_width + gap) // (card_width + gap))
    rows = int((page_height + gap) // (card_height + gap))
    cards_per_page = columns * rows
    grid_width = columns * card_width + (columns - 1) * gap
    grid_height = rows * card_height + (rows - 1) * gap
    left = (page_width - grid_width) / 2
    top = (page_height + grid_height) / 2
    pdf = canvas.Canvas(str(output_path), pagesize=A4, pageCompression=1)
    pdf.setTitle(Path(str(output_path)).stem + " card proxies")

    total_copies = sum(count for _, _, count in images)
    total_pages = (total_copies + cards_per_page - 1) // cards_per_page
    print(
        f"Creating PDF: {total_copies} card copies across {total_pages} "
        f"{'page' if total_pages == 1 else 'pages'}.",
        flush=True,
    )
    card_index = 0
    for card_number, (name, image, count) in enumerate(images, start=1):
        first_page = card_index // cards_per_page + 1
        last_page = (card_index + count - 1) // cards_per_page + 1
        page_label = (
            f"page {first_page}"
            if first_page == last_page
            else f"pages {first_page}-{last_page}"
        )
        print(
            f"[{card_number}/{len(images)}] {name}: "
            f"{count} {'copy' if count == 1 else 'copies'} ({page_label})",
            flush=True,
        )
        for _ in range(count):
            if card_index and card_index % cards_per_page == 0:
                pdf.showPage()
            slot = card_index % cards_per_page
            row, column = divmod(slot, columns)
            pdf.drawImage(
                image,
                left + column * (card_width + gap),
                top - card_height - row * (card_height + gap),
                width=card_width,
                height=card_height,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
            card_index += 1
    try:
        pdf.save()
        print(f"Saved PDF: {output_path}", flush=True)
        return output_path
    except PermissionError as e:
        print(f"Error saving PDF: {e}", flush=True)
        print("Please close the PDF if it is open in another program and try again.", flush=True)
        return None


if __name__ == "__main__":
    test_file = Path(__file__).resolve().parent.parent / "testing" / "mantis.txt"
    output_path = Path(__file__).resolve().parent.parent / "testing" / "mantis.pdf"

    file_contents = store_text_file_as_list(test_file)

    cards = load_cards(file_contents)
    result = create_proxy_pdf(cards, output_path)
    print(result)
