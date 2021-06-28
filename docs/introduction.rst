.. _introduction:

Introduction
=============================================

This package provides a python interface to the Jitsuin
Archivist.

The definitive guide to the REST API is defined here: https://jitsuin-archivist.readthedocs.io

This python SDK offers a number of advantages over a simple 
REST api (in any language):

    *  versioned package for the python 3.6,3.7,3.8,3.9 ecosystem.
    *  automatic confirmation of assets and events: just set **confirm=True** when
       creating the asset or event and a sophisticated retry and exponential backoff
       algorithm will take care of everything.
    *  simple **count()** method: one can easily get a count of assets or events that
       correspond to a particular signature.
    *  a **wait_for_confirmed()** method that waits for all assets or events that meet
       certain criteria to become confirmed.
    *  a **read_by_signature()** method that allows one to retrieve an asset or evenst with a 
       unique signature without knowing the identity.
    *  comprehensive exception handling - clear specific exceptions.
    *  easily extensible - obeys the open-closed principle of SOLID where new endpoints 
       can be implemented by **extending** the package as opposed to modifying it.
    *  fully unittested - 100% coverage.
    *  code style managed and enforced. 

See the **examples/** directory for example code.

Logging
=======

Follows the Django model as described here: https://docs.djangoproject.com/en/3.2/topics/logging/

The base logger for this package is rooted at "archivist" with subloggers for each endpoint:

    - "archivist.archivist"
    - "archivist.assets"
    - ...

etc. etc.

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

