from typing import Callable, Any

def notify_and_exit(s: str = "Press Enter to exit."):
    '''Raises SystemExit after notifying the user.'''
    input(s)
    raise SystemExit

def input_until_valid(
    message,
    func: Callable[[str], bool],
    repeat_message = ""
):
    '''Asks for input until the given lambda function is true.'''
    choice = None
    first_ask = True
    while (not func(choice)):
        if not first_ask:
            if repeat_message:
                message = repeat_message

        choice = input(message).strip()

        first_ask = False

    return choice

def in_range(c: str, start, end):
    '''Returns whether a string is numeric and in the given range'''
    try:
        val = float(c)
        return start <= val < end
    except (ValueError, TypeError):
        return False

def yes_or_no(c: str):
    return (
        c is not None and
        c.lower() in ['y', 'n']
    )

def numbered_list(
    data: dict | list,
    start_at_0 = False,
    prefix: str | Callable[[Any], str] = "",
    suffix: str | Callable[[Any], str] = ""
) -> str:
    '''
    Returns a numbered list of the data.
    Affixes can be strings or lambda functions of the data key.
    '''
    s = ""
    i = int(not start_at_0)
    for item in data:
        pre = prefix(item) if callable(prefix) else prefix
        suf = suffix(item) if callable(suffix) else suffix

        s += f"{i}. {pre}{item}{suf}"

        if i != len(data):
            s += "\n"

        i += 1

    return s
