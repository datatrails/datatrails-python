.. _story_runnerindex:

Story Runner
.....................

A runner attribute of the archivist instance allows running scenarios from
a dictionary. Usually the dictionary is read from a yaml or json file.

.. literalinclude:: ../../examples/runner.py
   :language: python


This functionality is also available with the CLI tool :code:`archivist_runner`, which is bundled with version v0.10 onwards of the :code:`jitsuin-archivist` PIP installation.

See the `installation instructions`_ for more information.

.. _installation instructions: https://python.rkvst.com/index.html#installation

You can verify the installation by running the following:

.. code-block:: shell

   archivist_runner -h

Which will show you the available options when using :code:`archivist_runner`.

To use the :code:`archivist_runner` command you will need the following:

    - A Client ID and Client Secret by creating an `App Registration`_
    - The YAML file with the operations you wish to run
    - The URL of your RKVST instance, this is typically `https://app.rkvst.io`

.. _App Registration: https://docs.rkvst.com/docs/setup-and-administration/getting-access-tokens-using-app-registrations/

Example usage:

.. code-block:: shell

   archivist_runner \
         -u https://app.rkvst.io \
         --client-id <your-client-id> \
         --client-secret <your-client-secret> \
         functests/test_resources/richness_story.yaml

For further reading:

   - :ref:`executing_demo_ref` for an example of how to build your YAML file
   - :ref:`executing_template_demo_ref` for extending functionality with templating.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   execute
   execute_template
   generic
   assets_count
   assets_create
   assets_create_if_not_exists
   assets_list
   assets_wait_for_confirmed
   compliance_compliant_at
   compliance_policies_create
   composite_estate_info
   events_count
   events_create
   events_list
   locations_count
   locations_create
   locations_list
   subjects_count.rst
   subjects_create.rst
   subjects_create_b64.rst
   subjects_list.rst
   subjects_read.rst
   subjects_update.rst
   subjects_wait_for_confirmation.rst
   
   compliance_policies_demo
   compliance_policies_demo_dynamic_tolerance
   compliance_policies_demo_richness
   door_entry_demo
   estate_info_demo
   sbom_demo
   synsation_demo
   wipp_demo
