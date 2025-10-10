import itertools

def dict_product(d):
    keys = []
    values = []
    for k, v in d.items():
        if isinstance(v, dict):
            sub = dict_product(v)
            keys.append(k)
            values.append(sub)
        elif isinstance(v, list):
            keys.append(k)
            values.append(v)
        else:
            keys.append(k)
            values.append([v])
    for prod in itertools.product(*values):
        yield dict(zip(keys, prod))