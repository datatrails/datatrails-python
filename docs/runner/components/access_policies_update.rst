.. _access_policies_update_yamlref:

Access Policies Update Story Runner YAML
.........................................

:code:`access_policy_label` is required.

:code:`display_name`, :code:`filters` and :code:`access_permissions` are 
optional but at least one must be specified.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_UPDATE
          description: Update a access_policies entity.
          print_response: true
          archivist_label: Acme Corporation
          subject_label: An access policy
        display_name: An access policy
        filters:
        access_permissions:
