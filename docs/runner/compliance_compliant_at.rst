.. _compliance_compliant_at_yamlref:

Compliance Compliant_at Story Runner YAML
...........................................

'asset_label' is required from a previously created asset. The asset_id is retrieved and
inserted as the first argument to compliance.compliant_at().

'report' = true will cause a report to be printed on the compliance status.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: COMPLIANCE_COMPLIANT_AT
          description: Check Compliance of EV pump 1.
          report: true
          asset_label: ev pump 1
