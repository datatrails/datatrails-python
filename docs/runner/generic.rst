.. _generic_yamlref:

Generic Story Runner YAML
...........................................

Each step has some control values in the 'step' dictionary. Some of these values are
required, optional or required for a particular operation.

Each step follows the same pattern:

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ASSETS_CREATE
          description: Create new EV Pump with id 1.
          wait_time: 10
          print_response: true
          asset_name: Radiation bag 1
        ................definition of request body
  

:action:
    Required for every operation. This is a prefined constant that maps to
    a method e.g. "ASSETS_CREATE" will call the assets.create_from_data() method

:description:
    Optional but recommended.
    Emits this string to stdout.

:wait_time:
    The scenario will pause for this number of seconds before execution.
    Primarily used to demonstrate compliance policy evaluation. One pauses
    before creating events and before evaluating compliance to allow
    (for example) the asset to become non-compliant. (demonstration)

:print_response:
   Emit JSON representation of response. Useful for debugging purposes.

:asset_name:
   Required for 'EVENTS_CREATE' and 'COMPLIANCE_COMPLIANT_AT' operaions. Without
   this value these operations will fail.
   The asset_name is the 'attributes.arc_display_name' value of an asset.

