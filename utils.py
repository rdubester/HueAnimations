def flatten(lst):
    res = []
    for i in lst:
        if isinstance(i, list):
            res.extend(flatten(i))
        else:
            res.append(i)
    return res

def normalize(vals: list[float]):
    total = sum(vals)
    return [v / total for v in vals]

def strvals(vals: list):
    return ", ".join(str(v) for v in vals)

import time
def sleep_precise(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()
