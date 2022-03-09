.. _assets_create_yamlref:

Assets Create Story Runner YAML
.........................................

'asset_label' is not required but if unspecified the created asset will
not be accessible to later actions in the story.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE
          description: Create new EV Pump with id 1.
          asset_label: ev pump 1
        behaviours:
          - Attachments
          - RecordEvidence
        attributes:
          arc_display_name: ev pump 1
          arc_display_type: pump
          arc_namespace: wipp
          ev_pump: "true"
        confirm: true
