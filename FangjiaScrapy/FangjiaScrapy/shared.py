def safe_list_get(l, idx, default=None):
    return l[idx] if len(l) > idx else default


def safe_list_get_first(l, default=None):
    return l[0] if len(l) > 0 else default


class BulkBuffer(object):
    # This buffer for the bulk insertion
    global items_buffer
    items_buffer = []

    # Append item to the list
    def add(self, item):
        global items_buffer
        items_buffer.append(item)

    # Get the length of the item
    def get_len(self):
        global items_buffer
        return len(items_buffer)

    # Get the items list
    def get_all(self):
        global items_buffer
        return items_buffer

    # Empty the list
    def empty(self):
        global items_buffer
        items_buffer[:] = []
