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
    errors = []

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

    if text_ctrl_object is not None:
        text_ctrl_object.WriteText(f"Dynasty count: {dynasty_count}, Fate count: {fate_count}, Special count: {special_count}\n")
    else:
        print(f"Dynasty count: {dynasty_count}, Fate count: {fate_count}, Special count: {special_count}")

    if dynasty_count < 40:
        errors.append(f"Deck has {dynasty_count} dynasty cards; minimum is 40.")
    if fate_count < 40:
        errors.append(f"Deck has {fate_count} fate cards; minimum is 40.")
    if special_count < 1:
        errors.append(f"Deck has {special_count} special cards; minimum is 1.")

    return errors