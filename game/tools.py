from math import sqrt
from functools import wraps


def memoize(function):
    memo = {}
    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper

def distance(p):
    return p[0]**2 + p[1]**2

def get_distance(p1, p2):
    return sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def get_xy_from_index(i, num_cols):
    return i%num_cols, i/num_cols

def generate_N2(limit=None):
    ymax = [0]
    d = 0
    while limit is None or d <= limit:
        yieldable = []
        while True:
            batch = []
            for x in range(d+1):
                y = ymax[x]
                if distance((x, y)) <= d**2:
                    batch.append((x, y))
                    ymax[x] += 1
            if not batch:
                break
            yieldable += batch
        yieldable.sort(key=distance)
        for p in yieldable:
            yield p
        d += 1
        ymax.append(0)


def generate_Z2(limit=None, origin=(0, 0)):
    def origin_correction(final_p):
        return (final_p[0] + origin[0], final_p[1] + origin[1])
    for p in generate_N2(limit):
        yield origin_correction(p)
        if p[0] != 0:
            yield origin_correction((-p[0], p[1]))
        if p[1] != 0:
            yield origin_correction((p[0], -p[1]))
        if p[0] and p[1]:
            yield origin_correction((-p[0], -p[1]))

def get_tiles_by_row_snake(w, h, start="top left"):
    indexes = range(w*h)
    if start == "top left":
        for i, j in enumerate(indexes):
            if (j/w)%2:
                indexes[i] = ((j/w+1)*w - j%w) - 1
    else:
        pass
    return indexes