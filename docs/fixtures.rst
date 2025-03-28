.. _fixturesref:

Fixtures (Common Attributes)
=============================================

One can specify common attributes when creating/counting/querying assets, events
and locations.

.. code-block:: python
    
    from copy import copy

    from archivist.archivist import Archivist
    from archivist.errors import ArchivistError
    
    # Oauth2 token that grants access
    with open(".auth_token", mode='r', encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()
    
    # Initialize connection to Archivist - for assets on immutable ledger.
    ledger = Archivist(
        "https://app.datatrails.ai",
        authtoken,
    )
    
    # lets define doors in our namespace that reside on the immutable ledger...
    doors = copy(ledger)
    doors.fixtures = {
        "assets": {
            "attributes": {
                "arc_display_type": "door",
                "arc_namespace": "project xyz",
            },
        },
    }

    # a red front door
    door = doors.assets.create(
        attrs={
            "arc_display_name": "front door",
            "colour": "red",
        },
    )

    # a green back door
    door = doors.assets.create(
        attrs={
            "arc_display_name": "back door",
            "colour": "green",
        },
    )

    # no need to specify arc_display_type...
    no_of_doors = doors.assets.count()
    for d in doors.assets.list():
        print(d)


