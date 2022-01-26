.. _assets_create_yamlref:

Assets Create Story Runner YAML
.........................................

No required parameters except that the arc_diaplay_name value must be
specified and used as the 'asset_name' value on both 'EVENTS_CREATE' and
'COMPLIANCE_COMPLIANT_AT' operations.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE
          description: Create new EV Pump with id 1.
        behaviours:
          - Attachments
          - RecordEvidence
        attributes:
          arc_display_name: ev pump 1
          ev_pump: "true"
        confirm: true
