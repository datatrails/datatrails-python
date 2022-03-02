.. _assets_list_yamlref:

Assets List Story Runner YAML
.........................................

List all assets that have the required signature - in this example a listing of
all doors is output.

The 'print_response' setting should be specified as True in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_LIST
          description: List all doors
          print_response: true
        attrs:
          arc_display_type: door
