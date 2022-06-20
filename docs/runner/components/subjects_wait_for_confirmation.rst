.. _subjects_wait_for_confirmation:

Subjects Wait For Confirmation Story Runner YAML
.................................................

Wait for a subject to be confirmed.

'subject_label' is required.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: SUBJECTS_WAIT_FOR_CONFIRMATION
          description: Wait for all subjects to be confirmed
          print_response: true
          subject_label: A subject
