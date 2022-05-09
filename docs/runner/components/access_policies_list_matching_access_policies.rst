.. _access_policies_list_matching_access_policiesyamlref:

Access Policies List Matching AccessPolicies Story Runner YAML
...............................................................

List all access policies that match an asset.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_LIST_MATCHING_ACCESS_POLICIES
          description: List all access policies that match an asset
          print_response: true
          archivist_label: Acme Corporation
          asset_label: an asset
