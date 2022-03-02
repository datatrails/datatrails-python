.. _assets_count_yamlref:

Assets Count Story Runner YAML
.........................................

Count all assets that have the required signature - in this example a count of
all doors is output.

The 'print_response' setting should be specified as True in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_COUNT
          description: Count all doors
          print_response: true
        attrs:
          arc_display_type: door
