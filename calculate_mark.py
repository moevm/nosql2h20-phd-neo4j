_mark_3 = [(0, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]

_mark_4 = [(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8),
           (3, 3), (3, 5),
           (4, 2), (4, 4), (4, 6),
           (5, 7),
           (6, 1), (6, 3), (6, 5), (6, 7)]

_mark_5 = [(1, 1),
           (7, 2), (7, 4), (7, 6),
           (8, 3), (8, 5), (8, 7),
           (9, 7)]


def calc_mark(works):
    """
    :param works: int: (work_id, semester)
    """
    mark = 2

    found = 0
    print(works)
    for id, semester in works:
        if (id, semester) in _mark_3:
            found += 1
    print(f"Found is {found}")
    if found == len(_mark_3):
        mark += 1
    else:
        return mark

    found = 0
    for id, semester in works:
        if (id, semester) in _mark_4:
            found += 1
    if found == len(_mark_4):
        mark += 1
    else:
        return mark

    found = 0
    for id, semester in works:
        if (id, semester) in _mark_5:
            found += 1
    if found == len(_mark_5):
        mark += 1

    return mark
