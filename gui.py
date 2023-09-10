def get_double_jump_message(arcade, callback, manager):
    """
    The pop_up message call when we got the double_jump skill
    The code below opens the message box and auto-dismisses it when done.
    """
    message_box = arcade.gui.UIMessageBox(

        width=180,
        height=110,
        message_text=(
            "You got a new skill!\n"
            "DOUBLE JUMP!"
        ),
        callback=callback,
        buttons=["Ok"]
    )

    manager.add(message_box)
