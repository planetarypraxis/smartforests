def safe_to_int(x, default=None):
    try:
        return int(x)
    except:
        return default


def ensure_list(possible):
    if is_sequence(possible):
        return possible
    elif possible:
        return [possible]
    else:
        return []


def ensure_obj(possible):
    if possible is None:
        return {}

    return possible


def get(d, key, default=None):
    keys = ensure_list(key)
    val = None
    try:
        for key in keys:
            val = d.get(key)
            if val is not None:
                break
    except:
        pass
    try:
        if val is None:
            for key in keys:
                val = getattr(d, key)
                if val is not None:
                    break
    except:
        pass
    try:
        if val is None:
            for key in keys:
                val = getattr(ensure_obj(d), key)
                if val is not None:
                    break
    except:
        pass

    return val if val is not None else default


def get_path(d, *keys):
    for k in keys:
        d = get(d, k)
    return d


def is_sequence(arg):
    if isinstance(arg, str):
        return False
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
