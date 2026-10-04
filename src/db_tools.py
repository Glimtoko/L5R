from pathlib import Path
import sqlite3

def find_card(name: str) -> tuple[str, dict] | None:
    """Return the first matching (table name, card details), or None.

    Card names are matched exactly. Details map column names to stored values.
    """
    database_path = Path(__file__).resolve().parent.parent / "raw_data" / "cards.sqlite3"
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
            card = connection.execute(
                f'SELECT * FROM {quoted_table} WHERE "name" = ? LIMIT 1',
                (name,),
            ).fetchone()
            if card is not None:
                return table_name, dict(card)
        return None
    finally:
        connection.close()


if __name__ == "__main__":
    test_card = "Minor Illness"
    result = find_card(test_card)
    print(result)
