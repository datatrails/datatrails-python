
.. _loggerref:

Logger
--------------

The first (optional) call from the archivist package is to set the logger.

.. code:: python

    from archivist.logger import set_logger
    from archivist.archivist import Archivist

    set_logger("DEBUG")
    client_id = getenv("DATATRAILS_APPREG_CLIENT")
    client_secret_file = getenv("DATATRAILS_APPREG_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    arch = Archivist(
        "https://app.datatrails.ai",
        (client_id, client_secret),
    )


.. automodule:: archivist.logger
   :members:

