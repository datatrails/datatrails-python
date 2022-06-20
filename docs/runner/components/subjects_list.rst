.. _subjects_list_yamlref:

Subjects List Story Runner YAML
.........................................

List all subjects that have the required signature.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_LIST
          description: List all subjects
          print_response: true
        display_name: some subject
