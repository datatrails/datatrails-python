.. _locations_read_yamlref:

Locations Read Story Runner YAML
.........................................

Read the specified subject.

:code:`location_label` is required.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_READ
          description: Read location
          print_response: true
          archivist_label: Acme Corporation
          location_label: A subject
