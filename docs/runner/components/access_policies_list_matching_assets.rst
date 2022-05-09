.. _access_policies_list_matching_assetsyamlref:

Access Policies List Matching Assets Story Runner YAML
.......................................................

List all assets that match an access_policy.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_LIST_MATCHING_ASSETS
          description: List assets that match an access_policy
          print_response: true
          archivist_label: Acme Corporation
          access_policy_label: an access policy
