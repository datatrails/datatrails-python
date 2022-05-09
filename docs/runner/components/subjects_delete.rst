.. _subjects_delete_yamlref:

Subjects Delete Story Runner YAML
.........................................

Delete the specified subject.

:code:`subject_label` is required.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_DELETE
          description: Dele subject
          print_response: true
          archivist_label: Acme Corporation
          subject_label: A subject
