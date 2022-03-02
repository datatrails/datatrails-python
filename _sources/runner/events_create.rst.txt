.. _events_create_yamlref:

Events Create Story Runner YAML
...........................................

'asset_name' must match the arc_display_name attribute of an existing asset for which
the authorised Application Registration has Event write access

The 'attachments' setting uploads the attachment to archivist and the response
added to the event before posting.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_CREATE
          description: Access Card 2 opens Courts of justice front door
          asset_name: Access Card 2
          print_response: true
        operation: Record
        behaviour: RecordEvidence
        principal_declared:
          subject: courts.paris.wavestonedas
          email: courts.paris.wavestonedas@iot.wavestone.com
          display_name: Courts of Justice Paris Front Door machine credential
        event_attributes:
          arc_description: Opened Courts of Justice Paris Front Door
          arc_display_type: Door Open
          arc_evidence: ARQC 0x12345678
          arc_correlation_value: be5c8061-236d-4400-a625-b74a34e5801b
          wavestone_door_name: Courts of Justice Paris Front Door
          wavestone_evt_type: door_open
        attachments:
          - filename: functests/test_resources/doors/events/door_open.png
            content_type: image/png
        confirm: true
