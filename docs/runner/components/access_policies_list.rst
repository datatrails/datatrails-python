.. _access_policies_list_yamlref:

Access Policies List Story Runner YAML
.........................................

List all access_policies that have the required signature.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_LIST
          description: List all access_policies
          print_response: true
          archivist_label: Acme Corporation
        display_name: some access policy
