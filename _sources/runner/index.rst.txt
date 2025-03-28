.. _story_runnerindex:

Story Runner
.....................

A runner attribute of the archivist instance allows running scenarios from
a dictionary. Usually the dictionary is read from a yaml or json file.

.. literalinclude:: ../../examples/runner.py
   :language: python


This functionality is also available with the CLI tool :code:`archivist_runner`.

See the `installation instructions`_ for more information.

.. _installation instructions: https://python.datatrails.ai/index.html#installation

You can verify the installation by running the following:

.. code-block:: shell

   archivist_runner -h

Which will show you the available options when using :code:`archivist_runner`.

To use the :code:`archivist_runner` command you will need the following:

    - A Client ID and Client Secret by creating an `App Registration`_
    - The YAML file with the operations you wish to run
    - The URL of your DataTrails instance, this is typically `https://app.datatrails.ai`

.. _App Registration: https://docs.datatrails.ai/docs/setup-and-administration/getting-access-tokens-using-app-registrations/

Example usage:

.. code-block:: shell

   archivist_runner \
         -u https://app.datatrails.ai \
         --client-id <your-client-id> \
         --client-secret <your-client-secret> \
         functests/test_resources/subjects_story.yaml

For further reading:

   - :ref:`executing_demo_ref` for an example of how to build your YAML file
   - :ref:`executing_template_demo_ref` for extending functionality with templating.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   execute
   execute_template
   
   components/index
   demos/index
