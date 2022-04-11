.. _locations_count_yamlref:

Locations Count Story Runner YAML
.........................................

Count all locations that match criteria..

Setting :code:`print_response: true` is necessary to print the full result.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_COUNT
          description: Count location for which John Smith is director
          print_response: true
        attrs:
          director: John Smith
