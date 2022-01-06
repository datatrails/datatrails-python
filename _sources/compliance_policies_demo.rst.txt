.. _compliance_policies_demoref:

Compliance Policies Demo
...........................

The source code of a python script that reads a yaml file and executes
a Compliance Policy workflow.

Reference yaml files are available here:

    - :ref:`compliance_policies_demo_dynamic_toleranceref`
    - :ref:`compliance_policies_demo_richnessref`

To invoke this command:

    - obtain bearer token and put in file '.token'
    - choose which yaml file to use (of the 2 above)
    - get the URL of your Archivist instance

Execute:

.. code-block:: shell

   $ python3 \
         examples/compliance_demo.py \
         https://rkvst.io \
         .token \
         examples/compliance_stories/richness_story.yaml


.. literalinclude:: ../examples/compliance_demo.py
   :language: python



