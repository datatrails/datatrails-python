.. _access_policies_create_yamlref:

Access Policies Create Story Runner YAML
.........................................

:code:`access_policy_label` is not required but if unspecified the created access policy  will
not be accessible to later actions in the story.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ACCESS_POLICIES_CREATE
          description: Create an access_policy entity.
          print_response: true
          archivist_label: Acme Corporation
          access_policy_label: An access policy
        display_name: An access policy
        description: An access policy
        filters:
        access_permissions:
