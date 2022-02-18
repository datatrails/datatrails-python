.. _assets_create_if_not_exists_yamlref:

Assets Create If not exists Story Runner YAML
..............................................

Searches for an asset matching the given signature. Returns that asset if found,
else create a new one with the given signature and attributes

The 'signature' setting for both the asset and its associated location are required.
The 'location', 'attachments' and 'confirm' entries are optional.

The 'signature' for both asset and location will be merged into the attributes of
the created asset or location.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE_IF_NOT_EXISTS
          description: Create a door in Paris at Jitsuin offices.
        signature:
          attributes:
            arc_display_name: Jitsuin Paris Front Door
        behaviours:
          - RecordEvidence
          - Attachments
        attributes:
          arc_display_type: door
          arc_firmware_version: "1.0"
          arc_serial_number: das-j1-01
          arc_description: Electronic door entry system to Jitsuin France
          wavestone_asset_id: paris.france.jitsuin.das
        location:
          signature:
            display_name: Jitsuin Paris
          description: Sales and sales support for the French region
          latitude: 48.8339211
          longitude: 2.371345
          attributes:
            address: 5 Parvis Alan Turing, 75013 Paris, France
            wavestone_ext: managed
        attachments:
          - filename: functests/test_resources/doors/assets/entry_terminal.jpg
            content_type: image/jpg
        confirm: true
