def on_message_box_close(button_text):
    print(f"User pressed {button_text}.")


def get_double_jump_message(arcade_engine, ui_manager):
    """
    The pop_up message call when we got the double_jump skill
    The code below opens the message box and auto-dismisses it when done.
    """
    message_box = arcade_engine.gui.UIMessageBox(

        width=180,
        height=110,
        message_text=(
            "You got a new skill!\n"
            "DOUBLE JUMP!"
        ),
        buttons=["Ok"]
    )

    ui_manager.add(message_box)


def start_message(arcade_engine, ui_manager):
    """
    The pop_up message call when we start game
    The code below opens the message box and auto-dismisses it when done.
    """
    message_box = arcade_engine.gui.UIMessageBox(

        width=350,
        height=200,
        message_text=(
            "Управление:\n\n"
            "W и SPACE: Прыжок и Лестницы.\n"
            "A и стрелочка влево: движение в лево.\n"
            "W и стрелочка вправо: движение в право.\n\n"
            "В золотых сундуках новые навыки!"
        ),
        buttons=["Ok"]
    )

    ui_manager.add(message_box)