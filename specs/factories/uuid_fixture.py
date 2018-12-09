"""Manages uuids for tests in one file"""
UUIDS = ['dc5434f4-1239-41b2-87a1-c8df49f94ab2']
def get_uuid(index):
    """get a uuid, each index will be a new id.
    But always the same with each index"""
    return UUIDS[index]
