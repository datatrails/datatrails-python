.. _events_list_yamlref:

Events List Story Runner YAML
...........................................

'asset_label' must match the 'asset_label' field of a previous creation step
(ASSETS_CREATE or ASSETS_CREATE_IF_NOT_EXISTS)
for which the authorised Application Registration has Event write access

if 'asset_label' is not set, data for all assets is output.

'props', 'attrs' and 'asset_attrs' are optional.

This example lists all 'open door' events for the Courts of Justice Front Door.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_LIST
          description: List all events for Courts of Justice Paris Front Door
          print_response: true
          asset_label: Courts of Justice Paris Front Door
        props:
          confirmation_status: CONFIRMED
        attrs:
          arc_display_type: open
        asset_attrs:
          arc_display_type: door
