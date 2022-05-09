.. _access_policies_read_yamlref:

Access Policies Read Story Runner YAML
.........................................

Read the specified access_policy.

:code:`access_policy_label` is required.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_READ
          description: Read access_policy
          print_response: true
          archivist_label: Acme Corporation
          access_policy_label: An access policy
