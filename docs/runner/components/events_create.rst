.. _events_create_yamlref:

Events Create Story Runner YAML
...........................................

:code:`asset_label` must match the :code:`asset_label` setting when the asset was created in a previous
creation step (action is either :code:`ASSETS_CREATE` or :code:`ASSETS_CREATE_IF_NOT_EXISTS`).

The optional :code:`attachments` setting uploads the attachments to archivist and the response
added to the event before posting.

The optional :code:`sbom` setting uploads the sbom to archivist and the response added to the
event before posting. (see second example below)

:code:`confirm: true` means that the step will wait for the event to be completely created before moving on to the next step.
This is optional.

An example when opening a door in Paris:

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_CREATE
          description: Access Card 2 opens Courts of justice front door
          asset_label: Access Card 2
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
          wavestone_door_name: Courts of Justice Paris Front Door
          wavestone_evt_type: door_open
        attachments:
          - filename: functests/test_resources/doors/events/door_open.png
            content_type: image/png
        confirm: true


An example when releasing a software package as an sbom attachment:

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: EVENTS_CREATE
          description: Release YYYYMMDD.1 of Test SBOM for YAML story
          asset_label: ACME Corporation Detector SAAS
          print_response: true
        operation: Record
        behaviour: RecordEvidence
        event_attributes:
          arc_description: ACME Corporation Detector SAAS Released YYYYMMDD.1
          arc_display_type: Software Package Release
        attachments:
          - filename: functests/test_resources/sbom/gen1.xml
            content_type: text/xml
            display_name: ACME Generation1 SBOM
            type: Software Package Release
