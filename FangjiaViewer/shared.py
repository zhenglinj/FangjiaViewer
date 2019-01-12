def safe_list_get(l, idx, default=None):
    return l[idx] if len(l) > idx else default


def safe_list_get_first(l, default=None):
    return l[0] if len(l) > 0 else default
