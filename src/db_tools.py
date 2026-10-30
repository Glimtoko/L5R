from pathlib import Path
import sqlite3

def find_card(name: str, database="cards.sqlite3", text_ctrl_object=None) -> tuple[str, dict] | None:
    """Return the first matching (table name, card details), or None. Uses a fuzzy match on the card name, so "Minor Illness"
    will match "Minor Illness (2nd Edition)". Returns an eror message if multiple cards are found. The database is read-only.

    Card names are matched exactly. Details map column names to stored values.

    :param name: The card name to look up.
    :param database: The SQLite database file name (default: "cards.sqlite3").
    :param text_ctrl_object: Optional wx.TextCtrl object for logging messages.
    :return: A tuple of (table name, card details) if found, or None if not found or if multiple matches are found.
    """
    database_path = Path(__file__).resolve().parent.parent / "raw_data" / database
    connection = sqlite3.connect(database_path.as_uri() + "?mode=ro", uri=True)
    try:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        for table in tables:
            table_name = table["name"]
            quoted_table = '"' + table_name.replace('"', '""') + '"'
            columns = connection.execute(f"PRAGMA table_info({quoted_table})")
            if not any(column["name"] == "name" for column in columns):
                continue
            test = connection.execute(
                f'SELECT * FROM {quoted_table} WHERE "name" LIKE ?',
                (f"{name}%",),
            )
            all_cards = test.fetchall()
            if len(all_cards) > 1:
                if text_ctrl_object is not None:
                    text_ctrl_object.WriteText(f"Error: multiple cards found for '{name}' in table '{table_name}':\n")
                    for card in all_cards:
                        text_ctrl_object.WriteText(f"  - {card['name']}\n")
                else:
                    print(f"Error: multiple cards found for '{name}' in table '{table_name}':")
                    for card in all_cards:
                        print(f"  - {card['name']}")
                return None
            elif len(all_cards) == 1:
                card = all_cards[0]
                return table_name, dict(card)
        return None
    finally:
        connection.close()


if __name__ == "__main__":
    test_card = "Minor Illness"
    result = find_card(test_card)
    print(result)
