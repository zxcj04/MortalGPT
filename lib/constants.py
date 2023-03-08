from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class CallBackType:
    RESET: str = "reset"
    DONE: str = "done"


INLINE_KEYBOARD_MARKUP_RESET = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Reset", callback_data=CallBackType.RESET)],
    ]
)

INLINE_KEYBOARD_MARKUP_DONE = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Done", callback_data=CallBackType.DONE)],
    ]
)

DONE_STICKER = (
    "CAACAgQAAxkBAAIDuGQG7RK6Iuh1TTMrCiJXYPtumi88AAJhDQACkmP5UTcY0ZaIE93ELgQ"
)
