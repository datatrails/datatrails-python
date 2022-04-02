.. _subjects_create_yamlref:

Subjects Create Story Runner YAML
.........................................

'subject_label' is not required but if unspecified the created subject will
not be accessible to later actions in the story.

.. code-block:: yaml
    
    ---
    steps:
      - step:
        action: SUBJECTS_CREATE
        description: Create a subjects entity.
        print_response: true
        subject_label: A subject
      display_name: A subject
      wallet_pub_keys:
        - wallet_pub_key1
      tessera_pub_keys:
        - tessera_pub_key2
