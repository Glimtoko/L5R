import utils

dynasty_card_types = {
    'holding', 'personality', 'event'
}

fate_card_types = {
    'follower', 'item', 'ring', 'spell', 'strategy'
}

special_card_types = {
    'stronghold', 'wind'
}

def validate_deck(cards: dict[str, dict], text_ctrl_object=None) -> list[str]:
    """Validate a deck of cards and return a list of error messages.

    Ensures that the deck contains at least 40 dynasty cards, at least 40 fate cards, and at least 1 special card.
    """
    valid = True

    dynasty_count = sum(
        details['count'] for name, details in cards.items()
        if details['data'][0] in dynasty_card_types
        and name != "Bamboo Harvesters"  # Exclude Bamboo Harvesters from the dynasty count
        )

    fate_count = sum(details['count'] for name, details in cards.items() if details['data'][0] in fate_card_types)

    special_count = sum(
        details['count'] for name, details in cards.items()
        if details['data'][0] in special_card_types
        or name == "Bamboo Harvesters"  # Include Bamboo Harvesters in the special count
    )

    # Other checks
    for name, details in cards.items():
        count = details['count']
        unique = details['data'][1].get('unique', "false")
        unique = unique.lower() == "true"  # Convert to boolean
        if unique and count > 1:
            utils.message(text_ctrl_object, f"Deck has {count} copies of unique card {name}.")
            valid = False
        elif not unique and count > 3:
            utils.message(text_ctrl_object, f"Deck has {count} copies of non-unique card {name}.")
            valid = False

    if dynasty_count < 40:
        utils.message(text_ctrl_object, f"Deck has {dynasty_count} dynasty cards; minimum is 40.")
        valid = False
    if fate_count < 40:
        utils.message(text_ctrl_object, f"Deck has {fate_count} fate cards; minimum is 40.")
        valid = False
    if special_count < 1:
        utils.message(text_ctrl_object, f"Deck has {special_count} special cards; minimum is 1.")
        valid = False

    utils.message(
        text_ctrl_object,
        f"Dynasty count: {dynasty_count}, Fate count: {fate_count}, Special count: {special_count}"
    )

    return valid