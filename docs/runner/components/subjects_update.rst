.. _subjects_update_yamlref:

Subjects Update Story Runner YAML
.........................................

:code:`subject_label` is required.

:code:`display_name`, :code:`wallet_pub_key` and :code:`tessera_pub_key` are 
optional but at least one must be specified.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_UPDATE
          description: Update a subjects entity.
          print_response: true
          archivist_label: Acme Corporation
          subject_label: A subject
        display_name: A subject
        wallet_pub_key:
          - wallet_pub_key1
          - wallet_pub_key2
        tessera_pub_key:
          - tessera_pub_key1
          - tessera_pub_key2
