from log import get_logger

LOGGER = get_logger()


def find_special_unicode(prefix: str, text: str) -> str:
    index = text.find(prefix)
    if index == -1:
        raise ValueError("prefix not found!")
    special_char = text[index + len(prefix)]
    LOGGER.debug(
        f"Special Character Found after '{prefix}': '{special_char}' (Unicode: U+{ord(special_char):04X})"
    )
    return ord(special_char)
