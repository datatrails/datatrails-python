.. _events_list_yamlref:

Events List Story Runner YAML
...........................................

'asset_name' must match the arc_display_name attribute of an existing asset
for which the authorised Application Registration has Event write access

'props', 'attrs' and 'asset_attrs' are optional.

This example lists all 'open door' events for the Courts of Justice Front Door.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_LIST
          description: List all events for Courts of Justice Paris Front Door
          print_response: true
          asset_name: Courts of Justice Paris Front Door
        props:
          confirmation_status: CONFIRMED
        attrs:
          arc_display_type: open
        asset_attrs:
          arc_display_type: door
