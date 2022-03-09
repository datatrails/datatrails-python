.. _executing_template_demo_ref:

Example of templated runner code 
..................................

A more sophisticated usage using templated yaml files:

.. code-block:: shell

   $ archivist_template \
         -u https://app.rkvst.io \
         -t credentials/token \
         --namespace 1234567 \
         functests/test_resources/synsation_story.values.yaml \
         functests/test_resources/synsation_story.yaml.j2


