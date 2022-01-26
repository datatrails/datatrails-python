.. _runnerindex:

Story Runner
.........................

A runner attribute of the archivist instance allows running scenarios from
a dictionary. Usually the dictionary is read from a yaml or json file.

.. literalinclude:: ../../archivist/cmds/runner/run.py
   :language: python


This functionality is also available as a CLI 'archivist_runner'. After 
installation of the python wheel execute

.. code-block:: shell

   $ archivist_runner -h

to elucidate options.

To invoke this command:

    - obtain bearer token and put in file 'credentials/token'
    - choose which yaml file to use
    - get the URL of your Archivist instance

Execute:

.. code-block:: shell

   $ archivist_runner \
         -u https://app.rkvst.io \
         -t credentials/token \
         functests/test_resources/richness_story.yaml

See :ref:`compliance_policies_demoref` for example yaml files.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   generic
   assets_create
   compliance_compliant_at
   compliance_policies_create
   events.create
   
   compliance_policies_demo
   compliance_policies_demo_dynamic_tolerance
   compliance_policies_demo_richness
