.. _compliance_compliant_at_yamlref:

Compliance Compliant_at Story Runner YAML
...........................................

Verify an Asset against its compliance policies.

:code:`asset_label` is required from a previously created asset. The :code:`asset_id` is retrieved and
inserted as the first argument to :code:`compliance.compliant_at()`.

Setting :code:`report: true` will trigger a report to be printed on the compliance status.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: COMPLIANCE_COMPLIANT_AT
          description: Check Compliance of EV pump 1.
          report: true
          archivist_label: Acme Corporation
          asset_label: ev pump 1
