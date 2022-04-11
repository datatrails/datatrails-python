.. _generic_yamlref:

Generic Story Runner YAML
...........................................

Each step has some control values in the :code:`step` dictionary. Some of these values are
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
          asset_label: Radiation bag 1
          location_label: Cape Town
        ................definition of request body and other
                        parameters
  

:action:
    Required for every operation. This is a predefined constant that maps to
    a method e.g. "ASSETS_CREATE" will call the assets.create_from_data() method

:description:
    Optional but recommended.
    Emits this string to stdout.

:wait_time:
    The story runner will pause for this number of seconds before execution.
    Primarily used to demonstrate compliance policy evaluation. One pauses
    before creating events and before evaluating compliance to allow
    (for example) the asset to become non-compliant. (demonstration)

:print_response:
   Emit JSON representation of response. Useful for debugging purposes.

:asset_label:
   For create type actions (ASSETS_CREATE, ASSETS_CREATE_IF_NOT_EXISTS) the label is used
   by the runner to keep track of assets.

   For other actions which require access to an asset, this value is used as a key to
   obtain the identity of such a previously-created asset.

   In this way one can create assets and then refer to them in later steps of the story.

:location_label:
   For location create type actions (LOCATIONS_CREATE_IF_NOT_EXISTS) the label is used
   by the runner to keep track of locations.

   For other actions which require access to an location, this value is used as a key to
   obtain the identity of such a previously-created location.

   In this way one can create locations and then refer to them in later steps of the story.

