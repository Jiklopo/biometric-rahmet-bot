import re


def validate_kaspi(kaspi: str):
    if kaspi:
        r = re.match('(\+7[0-9]{10})|([0-9]{16})', kaspi)
        if r:
            return True
    return False
