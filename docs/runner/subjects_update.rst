.. _subjects_update_yamlref:

Subjects Update Story Runner YAML
.........................................

'subject_label' is required.

'display_name', wallet_pub_keys' and 'tessera_pub_keys' are 
optional but at least one must be specified.

.. code-block:: yaml
    
    ---
    steps:
      - step:
        action: SUBJECTS_UPDATE
        description: Update a subjects entity.
        print_response: true
        subject_label: A subject
      display_name: A subject
      wallet_pub_keys:
        - wallet_pub_key1
        - wallet_pub_key2
      tessera_pub_keys:
        - tessera_pub_key1
        - tessera_pub_key2
