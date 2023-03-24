from colorama import Fore, Style


def red(text) -> str:
    text = str(text)
    if text is not None:
        return Fore.RED + text + Fore.RESET
    else:
        return ''


def green(text) -> str:
    text = str(text)
    if text is not None:
        return Fore.GREEN + text + Fore.RESET
    else:
        return ''


def cyan(text) -> str:
    text = str(text)
    if text is not None:
        return Fore.CYAN + text + Fore.RESET
    else:
        return ''


def magenta(text) -> str:
    text = str(text)
    if text is not None:
        return Fore.MAGENTA + text + Fore.RESET
    else:
        return ''


def yellow(text) -> str:
    text = str(text)
    if text is not None:
        return Fore.YELLOW + text + Fore.RESET
    else:
        return ''


def bright(text) -> str:
    text = str(text)
    if text is not None:
        return Style.BRIGHT + text + Style.NORMAL
    else:
        return ''
