.. _assets_create_if_not_exists_yamlref:

Assets Create If not exists Story Runner YAML
..............................................

Searches for an asset matching the given selector and returns that asset if found,
otherwise it will create a new one with the given attributes.

:code:`asset_label` is not required but if unspecified the created asset will
not be accessible to later actions in the story.

The :code:`selector` setting for both the asset and its associated location are required.

The :code:`location`, :code:`attachments` and :code:`confirm` entries are optional.

The :code:`arc_namespace` (for the asset) and the :code:`namespace` (for the location) are used
to distinguish between assets and locations created between runs of the story.

Usually these field values are derived from an environment variable 
:code:`RKVST_UNIQUE_ID` (default value is :code:`namespace`).

:code:`confirm: true` means that the step will wait for the asset to be completely created before moving on to the next step.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE_IF_NOT_EXISTS
          description: Create a door in Paris at RKVST offices.
          asset_label: RKVST Paris Front Door
        selector:
          - attributes:
            - arc_display_name
            - arc_namespace
        behaviours:
          - RecordEvidence
        attributes:
          arc_display_name: RKVST Paris Front Door
          arc_namespace: door entry
          arc_display_type: door
          arc_firmware_version: v1.0
          arc_serial_number: das-j1-01
          arc_description: Electronic door entry system to RKVST France
          wavestone_asset_id: paris.france.rkvst.das
        location:
          selector:
            - display_name
            - attributes:
              - namespace
          display_name: RKVST Paris
          description: Sales and sales support for the French region
          latitude: 48.8339211
          longitude: 2.371345
          attributes:
            namespace: door entry
            address: 5 Parvis Alan Turing, 75013 Paris, France
            wavestone_ext: managed
        attachments:
          - filename: functests/test_resources/doors/assets/entry_terminal.jpg
            content_type: image/jpg
        confirm: true
