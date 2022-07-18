def as_list(x):
    if type(x) is list:
        return x
    return [x]

def as_set(x):
    if type(x) is set:
        return x
    return set(as_list(x))