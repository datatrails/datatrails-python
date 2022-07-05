.. _compliance_policies_create_yamlref:

Compliance Policy Create Story Runner YAML
...........................................

The specific fields required vary according to 
:code:`compliance_type` and is documented elsewhere.

This example is for a :code:`DYNAMIC_TOLERANCE` type policy.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: COMPLIANCE_POLICIES_CREATE
          description: Create a compliance policy that checks an EV pump maintenance requests are serviced within a reasonable time frame.
          print_response: true
        description: ev maintenance policy
        display_name: ev maintenance policy
        compliance_type: COMPLIANCE_DYNAMIC_TOLERANCE
        asset_filter:  
          - or: [ "attributes.ev_pump=true" ]
        event_display_type: Maintenance Requested
        closing_event_display_type: Maintenance Performed
        dynamic_window: 700
        dynamic_variability: 1.5


This example is for a :code:`RICHNESS` type policy.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: COMPLIANCE_POLICIES_CREATE
          description: Create a compliance policy that checks the radiation level of radiation bags is less than 7 rads.
          print_response: true
        description: radiation level safety policy
        display_name: radiation safety policy
        compliance_type: COMPLIANCE_RICHNESS
        asset_filter:
          - or: [ "attributes.radioactive=true" ]
        richness_assertions:
          - or: [ "radiation_level<7" ]
