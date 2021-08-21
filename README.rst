.. _readme:

Jitsuin Archivist Client
=========================

The standard Jitsuin Archivist python client.

Please note that the canonical API for Jitsuin Archivist is always the REST API
documented at https://docs.rkvst.com

Installation
=============

Use standard python pip utility:

.. code-block:: bash

    python3 -m pip install jitsuin-archivist

Example
=============

One can then use the examples code to create assets (see examples directory):

.. code-block:: python
    
    from archivist.archivist import Archivist
    from archivist.errors import ArchivistError
    from archivist.storage_integrity import StorageIntegrity
    
    # Oauth2 token that grants access
    with open(".auth_token", mode='r') as tokenfile:
        authtoken = tokenfile.read().strip()
    
    # Initialize connection to Archivist - the URL for production will be different to this URL
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
    )
    
    # Create a new asset
    attrs = {
        "arc_display_name": "display_name",  # Asset's display name in the user interface
        "arc_description": "display_description",  # Asset's description in the user interface
        "arc_display_type": "desplay_type",  # Arc_display_type is a free text field
                                             # allowing the creator of
                                             # an asset to specify the asset
                                             # type or class. Be careful when setting this:
                                             # assets are grouped by type and
                                             # sharing policies can be
                                             # configured to share assets based on
                                             # their arc_display_type.
                                             # So a mistake here can result in asset data being
                                             # under- or over-shared.
            "some_custom_attribute": "value"  # You can add any custom value as long as
                                          # it does not start with arc_
    }
    #
    # store asset on the DLT or not. If DLT is not enabled for the user an error will occur if
    # StorageIntegrity.LEDGER is specified. If unspecified then TENANT_STORAGE is used
    # i.e. not stored on the DLT...
    # storage_integrity = StorageIntegrity.TENANT_STORAGE
    props = {
        "storage_integrity": StorageIntegrity.LEDGER.name,
    }

    # The first argument is the properties of the asset
    # The second argument is the attributes of the asset
    # The third argument is wait for confirmation:
    #   If @confirm@ is True then this function will not
    #   return until the asset is confirmed on the blockchain and ready
    #   to accept events (or an error occurs)
    #   After an asset is submitted to the blockchain (submitted),
    #   it will be in the "Pending" status.
    #   Once it is added to the blockchain, the status will be changed to "Confirmed"
    try:
        asset = arch.assets.create(props=props, attrs=attrs, confirm=True)
    except Archivisterror as ex:
        print("error", ex)
    else:
        print("asset", asset)
    

Logging
========

Follows the Django model as described here: https://docs.djangoproject.com/en/3.2/topics/logging/

The base logger for this package is rooted at "archivist" with subloggers for each endpoint:

.. note::
    archivist.archivist
        sublogger for archivist submodule

    archivist.assets
        sublogger for assets submodule

and for other endpoints.

Logging is configured by either defining a root logger with suitable handlers, formatters etc. or
by using dictionary configuration as described here: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

A recommended minimum configuration would be:

.. code-block:: python
    
    import logging
    
    logging.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    })

