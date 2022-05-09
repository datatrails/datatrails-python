.. _assets_create_yamlref:

Assets Create Story Runner YAML
.........................................

A simple Asset Creation Example.

:code:`asset_label` is not required but if unspecified the created asset will
not be accessible to later actions in the story.

The :code:`arc_namespace` (for the asset) and the :code:`namespace` (for the location) are used
to distinguish between assets and locations created between runs of the story.

Usually these field values are derived from an environment variable 
:code:`ARCHIVIST_NAMESPACE` (default value is :code:`namespace`).

The optional :code:`confirm: true` entry means that the step will wait for the asset to be completely created before moving on to the next step.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE
          description: Create new EV Pump with id 1.
          archivist_label: Acme Corporation
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
