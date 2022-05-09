.. _access_policies_count_yamlref:

Access Policies Count Story Runner YAML
.........................................

Count all access_policies that have the required signature.

The :code:`archivist_label` is required.

The :code:`display_name` is optional.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_COUNT
          description: Count all access_policies
          print_response: true
          archivist_label: Acme Corporation
        display_name: some access_policy
