.. _assets_list_yamlref:

Assets List Story Runner YAML
.........................................

List all assets that have the required signature - in this example a listing of
all doors is output.

Setting :code:`print_response: true` is necessary to print the full result.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_LIST
          description: List all doors
          print_response: true
          archivist_label: Acme Corporation
        attrs:
          arc_display_type: door
          arc_namespace: door entry
