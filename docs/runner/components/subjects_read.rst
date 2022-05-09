.. _subjects_read_yamlref:

Subjects Read Story Runner YAML
.........................................

Read the specified subject.

:code:`subject_label` is required.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_READ
          description: Read subject
          print_response: true
          archivist_label: Acme Corporation
          subject_label: A subject
