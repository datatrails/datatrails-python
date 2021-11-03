"""Archivist OR dictionary and list

   Used in filters: list of Or dictionaries

   Dictionaries where key is always 'or' and value is a list of strings
"""


def or_dict(list_):
    """Construct a dictionary with key 'or'"""
    return {"or": list_}


def and_list(lists):
    """Construct a list of or dictionaries"""
    return [or_dict(j) for j in lists]
