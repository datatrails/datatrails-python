.. _events_count_yamlref:

Events Count Story Runner YAML
...........................................

:code:`asset_label` must match the :code:`asset_label` field of a previous creation step
(:code:`ASSETS_CREATE` or :code:`ASSETS_CREATE_IF_NOT_EXISTS`) 
for which the authorized credentials have Event write access.

:code:`props`, :code:`attrs` and :code:`asset_attrs` are optional.

This example counts all 'open door' events for the Courts of Justice Front Door.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_COUNT
          description: List all events for Courts of Justice Paris Front Door
          print_response: true
          archivist_label: Acme Corporation
          asset_label: Courts of Justice Paris Front Door
        props:
          confirmation_status: CONFIRMED
        attrs:
          arc_display_type: open
        asset_attrs:
          arc_display_type: door
