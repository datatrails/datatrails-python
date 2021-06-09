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
