def message(text_ctrl_object, message):
    """
    Writes a message to the provided text control object if it is not None.
    If the text control object is None, it prints the message to the console.
    """
    if text_ctrl_object is not None:
        text_ctrl_object.WriteText(message + "\n")
    else:
        print(message, flush=True)