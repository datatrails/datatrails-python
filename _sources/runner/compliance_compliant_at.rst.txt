.. _compliance_compliant_at_yamlref:

Compliance Compliant_at Story Runner YAML
...........................................

'asset_name' is required from a previously created asset. The asset_id is derived and
inserted as the first argument to compliance.compliant_at().

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: COMPLIANCE_COMPLIANT_AT
          description: Check Compliance of EV pump 1.
          asset_name: ev pump 1
