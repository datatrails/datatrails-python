.. _locations_count_yamlref:

Locations Count Story Runner YAML
.........................................

Count all locations that match criteria..

The 'print_response' setting should be specified as True in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_COUNT
          description: Count location for which John Smith is director
          print_response: true
        attrs:
          director: John Smith
