.. _subjects_count_yamlref:

Subjects Count Story Runner YAML
.........................................

Count all subjects that have the required signature.

The :code:`display_name` is optional.

The :code:`print_response` setting should be specified as :code:`True` in order to see the results.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_COUNT
          description: Count all subjects
          print_response: true
        display_name: some subject
