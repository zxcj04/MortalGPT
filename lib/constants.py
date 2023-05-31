import string

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import zhon.hanzi
from opencc import OpenCC

PUNCTUATIONS = [
    *string.punctuation,
    *zhon.hanzi.punctuation,
    "\n",
    "\n\n",
    "\r",
    "\r\n",
]

CC = OpenCC("s2t")


class CallBackType:
    RESET: str = "reset"
    DONE: str = "done"
    RETRY: str = "retry"


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

INLINE_KEYBOARD_MARKUP_RETRY = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Retry", callback_data=CallBackType.RETRY)],
    ]
)

INLINE_KEYBOARD_MARKUP_DONE_RETRY = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Done", callback_data=CallBackType.DONE),
            InlineKeyboardButton("Retry", callback_data=CallBackType.RETRY),
        ],
    ]
)

INLINE_KEYBOARD_MARKUP_RETRY_RESET = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Retry", callback_data=CallBackType.RETRY),
            InlineKeyboardButton("Reset", callback_data=CallBackType.RESET),
        ],
    ]
)

DONE_STICKER = (
    "CAACAgQAAxkBAAIDuGQG7RK6Iuh1TTMrCiJXYPtumi88AAJhDQACkmP5UTcY0ZaIE93ELgQ"
)
