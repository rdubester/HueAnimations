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