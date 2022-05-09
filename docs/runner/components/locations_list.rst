.. _locations_list_yamlref:

Locations List Story Runner YAML
.........................................

List all locations that match criteria..

Setting :code:`print_response: true` is necessary to print the full result.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_LIST
          description: List locations for which John Smith is director
          print_response: true
          archivist_label: Acme Corporation
        attrs:
          director: John Smith
