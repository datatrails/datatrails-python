.. _featuresref:

Features
=============================================

This package provides a python interface to DATATRAILS.

The definitive guide to the REST API is defined here: https://docs.datatrails.ai

This python SDK offers a number of advantages over a simple 
REST api (in any language):

    *  versioned package for the python 3.9,3.10,3.11,3.12,3.13 ecosystems.
    *  automatic confirmation of assets and events: just set **confirm=True** when
       creating the asset or event and a sophisticated retry and exponential backoff
       algorithm will take care of everything (optional).
    *  **list()** method: one can easily get an iterable of assets or events that
       correspond to a particular signature. The list method is optimized for use in
       loop (for a in arch.assets.list():...) but can easily be converted to a list
       using the python list() function.
    *  simple **count()** method: one can easily get a count of assets or events that
       correspond to a particular signature.
    *  a **wait_for_confirmed()** method that waits for all assets or events that meet
       certain criteria to become confirmed.
    *  a **read_by_signature()** method that allows one to retrieve an asset or event with a 
       unique signature without knowing the identity.
    *  predefined **fixtures** that allow specifying common attributes of assets/events
    *  a story runner where a yaml file can be used to exercise the various methods in
       the PythonSDK.
    *  comprehensive exception handling - clear specific exceptions.
    *  easily extensible - obeys the open-closed principle of SOLID where new endpoints 
       can be implemented by **extending** the package as opposed to modifying it.
    *  fully unittested - 100% coverage.
    *  code style managed and enforced using **ruff**, **pycodestyle**, **pylint** and **black**. 

See the **examples/** directory for example code.
