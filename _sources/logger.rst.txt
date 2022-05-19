
.. _loggerref:

Logger
--------------

The first (optional) call from the archivist package is to set the logger.

.. code:: python

    from archivist.logger import set_logger
    from archivist.archivist import Archivist

    set_logger("DEBUG")
    client_id = getenv("ARCHIVIST_CLIENT_ID")
    client_secret_file = getenv("ARCHIVIST_CLIENT_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    arch = Archivist(
        "https://app.rkvst.io",
        (client_id, client_secret),
        max_time=300,
    )


.. automodule:: archivist.logger
   :members:

