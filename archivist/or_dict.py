"""Archivist OR dictionary and list

   Used in filters: list of Or dictionaries

   Dictionaries where key is always 'or' and value is a list of strings
"""


from typing import Any


def or_dict(list_: list) -> "dict[str, list]":
    """Construct a dictionary with key 'or'"""
    return {"or": list_}


def and_list(lists: list) -> "list[dict[str, list[Any]]]":
    """Construct a list of or dictionaries"""
    return [or_dict(j) for j in lists]
