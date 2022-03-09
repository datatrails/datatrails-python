.. _assets_wait_for_confirmed_yamlref:

Assets Wait For Confirmed Story Runner YAML
............................................

Wait for all assets that have the required signature to be confirmed.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_WAIT_FOR_CONFIRMED
          description: Wait for all assets to be confirmed
        attrs:
          arc_namespace: synsation
