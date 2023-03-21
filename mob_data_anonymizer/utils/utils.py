def inclusive_range(start, stop, step):
    if step:
        return range(start, (stop + 1) if step >= 0 else (stop - 1), step)
    else:
        return range(start, stop + 1)


def round_tuple(t: tuple, precision: int = 2):
    r = [round(v, precision) for v in t]

    return tuple(r)
