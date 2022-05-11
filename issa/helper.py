from ast import arg


def create_dict(arg1: list) -> dict:
    freq = 0
    for band in arg1:
        freq = band[2]
    return freq