from pathlib import Path
from pprint import pprint
import xml.etree.ElementTree as ET
import sys
import json
import sqlite3

print(sys.version)

input_name = "three_dynasties.xml"
legality = "three_dynasties"
output = "three_dynasties.sqlite3"


database = ET.parse(Path(__file__).with_name(input_name))

cards = [
    card
    for card in database.iter("card")
    if any(legal.text == legality for legal in card.findall("legal"))
]

card_types = sorted({card.attrib["type"] for card in cards})
print(card_types)
print(len(card_types))

# Each child element maps to the set of attribute names observed on it.
card_contents = {}
for card in cards:
    elements = card_contents.setdefault(card.attrib["type"], {})
    for child in card:
        print(child.tag, child.attrib)
        elements.setdefault(child.tag, set()).update(child.attrib)
    elements.setdefault("unique", False)

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

sqlite_path = Path(__file__).with_name(output)
with sqlite3.connect(sqlite_path) as connection:
    for card_type, elements in card_contents.items():
        table = quote_identifier(card_type)
        names = sorted(elements)
        columns = ["id", *names]
        print(f"Creating table {table} with columns: {columns}")
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
        print(f"Insert SQL: {insert_sql}")
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

            values[-1] = "False"  # Set the last value (unique) to "False"
            try:
                text = values[-2]
            except IndexError:
                pass
            else:
                if "Unique" in text:
                    values[-1] = "True"
            # values.append("False")
            print(len(values))
            connection.execute(insert_sql, values)
            count += 1
        print(f"{card_type}: imported {count} cards")

print(f"Database saved to {sqlite_path}")
