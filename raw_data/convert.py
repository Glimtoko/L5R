from pathlib import Path
from pprint import pprint
import xml.etree.ElementTree as ET
import sys
import json
import sqlite3

print(sys.version)

database = ET.parse(Path(__file__).with_name("database.xml"))

cards = [
    card
    for card in database.iter("card")
    if any(legal.text == "shattered_empire" for legal in card.findall("legal"))
]

card_types = sorted({card.attrib["type"] for card in cards})
print(card_types)
print(len(card_types))

# Each child element maps to the set of attribute names observed on it.
card_contents = {}
for card in cards:
    elements = card_contents.setdefault(card.attrib["type"], {})
    for child in card:
        elements.setdefault(child.tag, set()).update(child.attrib)

pprint(card_contents)


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


# Use the same representation for an element throughout each card type.
json_elements = {
    card_type: {
        name
        for name, attributes in elements.items()
        if attributes or any(
            len(card.findall(name)) > 1
            for card in cards if card.attrib["type"] == card_type
        )
    }
    for card_type, elements in card_contents.items()
}

sqlite_path = Path(__file__).with_name("cards.sqlite3")
with sqlite3.connect(sqlite_path) as connection:
    for card_type, elements in card_contents.items():
        table = quote_identifier(card_type)
        names = sorted(elements)
        columns = ["id", *names]
        definitions = ['"id" TEXT PRIMARY KEY'] + [
            f"{quote_identifier(name)} TEXT" for name in names
        ]
        connection.execute(
            f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(definitions)})"
        )
        insert_sql = (
            f"INSERT OR REPLACE INTO {table} "
            f"({', '.join(quote_identifier(name) for name in columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)})"
        )
        count = 0
        for card in cards:
            if card.attrib["type"] != card_type:
                continue
            values = [card.attrib["id"]]
            for name in names:
                children = card.findall(name)
                if not children:
                    values.append(None)
                elif name in json_elements[card_type]:
                    values.append(json.dumps([
                        {"text": child.text, "attributes": dict(child.attrib)}
                        for child in children
                    ], ensure_ascii=False))
                else:
                    values.append(children[0].text)
            connection.execute(insert_sql, values)
            count += 1
        print(f"{card_type}: imported {count} cards")

print(f"Database saved to {sqlite_path}")
