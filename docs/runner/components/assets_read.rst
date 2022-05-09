.. _assets_read_yamlref:

Assets Read Story Runner YAML
.........................................

Read the specified subject.

:code:`asset_label` is required.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_READ
          description: Read asset
          print_response: true
          archivist_label: Acme Corporation
          asset_label: An asset
