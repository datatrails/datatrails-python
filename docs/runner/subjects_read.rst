.. _subjects_read_yamlref:

Subjects Read Story Runner YAML
.........................................

Read the specified subject.

'subject_label' is required.

The 'print_response' setting should be specified as True in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_READ
          description: Read subject
          print_response: true
          subject_label: A subject
