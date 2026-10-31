import utils

def validate_deck(cards: dict[str, dict], text_ctrl_object=None) -> bool:
    """Validate a deck of cards and return a list of error messages.

    Ensures that the deck contains at least 40 dynasty cards, at least 40 fate cards,
    and at least 1 special card. Also checks that unique cards do not exceed 1 copy
    and non-unique cards do not exceed 3 copies.

    :param cards: A dictionary where keys are card names and values are dictionaries
                  containing 'count' and 'data' (which includes card type and uniqueness).
    :param text_ctrl_object: The text control object for displaying messages.
    :return: True if the deck is valid, False otherwise.
    """

    dynasty_card_types = {'holding', 'personality', 'event'}
    fate_card_types = {'follower', 'item', 'ring', 'spell', 'strategy'}
    special_card_types = {'stronghold', 'wind'}

    valid = True
    special_count = 0
    fate_count = 0
    dynasty_count = 0

    for name, details in cards.items():
        count = details['count']
        data = details['data']

        # Check count against uniqueness and maximum allowed copies
        unique = data[1].get('unique', "false")
        unique = unique.lower() == "true"  # Convert to boolean
        if unique and count > 1:
            utils.message(text_ctrl_object, f"Deck has {count} copies of unique card {name}.")
            valid = False
        elif not unique and count > 3:
            utils.message(text_ctrl_object, f"Deck has {count} copies of non-unique card {name}.")
            valid = False

        # Count card types
        if data[0] in dynasty_card_types and name != "Bamboo Harvesters":
            dynasty_count += count
        elif data[0] in fate_card_types:
            fate_count += count
        elif data[0] in special_card_types or name == "Bamboo Harvesters":
            special_count += count

    if dynasty_count < 40:
        utils.message(text_ctrl_object, f"Error: Deck has {dynasty_count} dynasty cards; minimum is 40.")
        valid = False
    if fate_count < 40:
        utils.message(text_ctrl_object, f"Error: Deck has {fate_count} fate cards; minimum is 40.")
        valid = False
    if special_count < 1:
        utils.message(text_ctrl_object, f"Error: Deck has {special_count} special cards; minimum is 1.")
        valid = False

    utils.message(
        text_ctrl_object,
        f"Dynasty count: {dynasty_count}, Fate count: {fate_count}, Special count: {special_count}"
    )

    return valid