.. _events_create_yamlref:

Events Create Story Runner YAML
...........................................

'asset_name' is required from a previously created asset. The asset_id is derived and 
inserted as the first argument to events.create_from_data().

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_CREATE
          description: Create Event requesting EV pump 1 needs maintenance.
          asset_name: ev pump 1
        operation: Record
        behaviour: RecordEvidence
        event_attributes:
          arc_correlation_value: EV Maintenance 1
          arc_description: request maintenance
          arc_display_type: Maintenance Requested
        confirm: true
