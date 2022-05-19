def inclusive_range(start, stop, step):
    if step:
        return range(start, (stop + 1) if step >= 0 else (stop - 1), step)
    else:
        return range(start, stop + 1)