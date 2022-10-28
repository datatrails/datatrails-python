
.. _readme:

RKVST Python Client
=========================

The standard RKVST Python Client.

Please note that the canonical API for RKVST is always the REST API
documented at https://docs.rkvst.com

Support
=======

This package currently is tested against Python versions 3.7,3.8,3.9,3.10 and 3.11.

The current default version is 3.7 - this means that this package will not
use any features specific to versions 3.8 and later.

After End of Life of a particular Python version, support is offered on a best effort
basis. We may ask you to update your Python version to help solve the problem,
if it cannot be reasonably resolved in your current version.

Installation
=============

Use standard python pip utility:

.. code:: bash

    python3 -m pip install jitsuin-archivist

If your version of python3 is too old an error of this type or similar will be emitted:

.. note:: 

    ERROR: Could not find a version that satisfies the requirement jitsuin-archivist (from versions: none)
    ERROR: No matching distribution found for jitsuin-archivist

Example
=============

You can then use the examples code to create assets (see examples directory):

.. code:: python

    """Create an asset in RKVST with User Token.

    The module contains two functions: main and create_asset. Main function parses in
    a url to the Archivist and credentials, which is a user authorization.
    The main function would initialize an archivist connection using the url and
    the credentials, called "arch", then call arch.assets.create() and the asset will be created.
    """

    from os import getenv

    from archivist.archivist import Archivist
    from archivist.proof_mechanism import ProofMechanism


    def create_asset(arch):
        """Create an asset using Archivist Connection.

        Args:
            arch: archivist connection.

        Returns:
            newasset: a new asset created.

        """
        attrs = {
            "arc_display_name": "display_name",  # Asset's display name in the user interface
            "arc_description": "display_description",  # Asset's description in the user interface
            "arc_display_type": "display_type",  # Arc_display_type is a free text field
            # allowing the creator of
            # an asset to specify the asset
            # type or class. Be careful when setting this:
            # assets are grouped by type and
            # sharing policies can be
            # configured to share assets based on
            # their arc_display_type.
            # So a mistake here can result in asset data being
            # under- or over-shared.
            "some_custom_attribute": "value"  # You can add any custom value as long as
            # it does not start with arc_
        }
        #
        # Select the mechanism used to prove evidence for the asset.  If the selected proof
        # mechanism is not enabled for your tenant then an error will occur.
        # If unspecified then SIMPLE_HASH is used.
        # proof_mechanism = ProofMechanism.KHIPU.name
        props = {
            "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
        }

        # The first argument are the properties of the asset
        # The second argument are the attributes of the asset
        # The third argument is wait for confirmation:
        #   If @confirm@ is True then this function will not
        #   return until the asset is confirmed on the blockchain and ready
        #   to accept events (or an error occurs)
        #
        return arch.assets.create(props=props, attrs=attrs, confirm=True)
        # alternatively if some work can be done whilst the asset is confirmed then this call can be
        # replaced by a two-step alternative:

        # asset = arch.assets.create(props=props, attrs=attrs, confirm=False)

        # ... do something else here
        # and then wait for confirmation

        # self.arch.assets.wait_for_confirmation(asset['identity']))


    def main():
        """Main function of create asset.

        Parse in user input of url and client id/secrets and use them to
        create an example archivist connection and create an asset.

        """

        # client id and client secret is obtained from the appidp endpoint - see the
        # application registrations example code in examples/applications_registration.py
        #
        # client id is an environment variable. client_secret is stored in a file in a
        # directory that has 0700 permissions. The location of this file is set in
        # the client_secret_filename environment variable.
        client_id = getenv("ARCHIVIST_CLIENT_ID")
        client_secret_file = getenv("ARCHIVIST_CLIENT_SECRET_FILENAME")
        with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
            client_secret = tokenfile.read().strip()

        # Initialize connection to Archivist. max_time is the time to wait for confirmation
        # of an asset or event creation - the default is 1200 seconds but one can optionally
        # specify a different value here particularly when creating assets on SIMPLE_HASH
        # (rather than KHIPU) as confirmation times are much shorter in this case.
        with arch = Archivist(
            "https://app.rkvst.io",
            (client_id, client_secret),
            max_time=300,
        ) as arch:
            # Create a new asset
            asset = create_asset(arch)
            print("Asset", asset)


    if __name__ == "__main__":
        main()


Notebooks
=================

Some jupyter notebooks are available to exercise the examples code. Do the following:

.. code:: text

    task builder      # only necessary first time checking out repo.
    ./scripts/notebooks.sh

Something similar to the following will be emitted:

.. code:: text

    [I 2022-07-13 15:29:32.102 LabApp] JupyterLab extension loaded from /usr/local/lib/python3.7/site-packages/jupyterlab
    [I 2022-07-13 15:29:32.102 LabApp] JupyterLab application directory is /usr/local/share/jupyter/lab
    [I 15:29:32.106 NotebookApp] Serving notebooks from local directory: /home/builder/notebooks
    [I 15:29:32.107 NotebookApp] Jupyter Notebook 6.4.12 is running at:
    [I 15:29:32.107 NotebookApp] http://d77e9e7ff8a1:8888/?token=e51c0b5120f5cf76e06c0415896aee13b0849830a9c8c83f
    [I 15:29:32.107 NotebookApp]  or http://127.0.0.1:8888/?token=e51c0b5120f5cf76e06c0415896aee13b0849830a9c8c83f
    [I 15:29:32.107 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [C 15:29:32.110 NotebookApp]

        To access the notebook, open this file in a browser:
            file:///home/builder/.local/share/jupyter/runtime/nbserver-1-open.html
        Or copy and paste one of these URLs:
            http://d77e9e7ff8a1:8888/?token=e51c0b5120f5cf76e06c0415896aee13b0849830a9c8c83f
         or http://127.0.0.1:8888/?token=e51c0b5120f5cf76e06c0415896aee13b0849830a9c8c83f

Cut and paste one of the links given into your browser and use the various dialogs to select an available notebook
or create a new notebook and follow current code in examples directory.
Please note that security tokens will be required - either a JWT or Application ID and secret and these should be stored in files in the local credentials directory.


File Story Runner
=================

You can run scenarios - a sequence of steps - from a python dictionary or from a yaml
or json file.

Python
------

.. code:: python

    from logging import getLogger
    from pyaml_env import parse_config
    from sys import exit as sys_exit
    from sys import stdout as sys_stdout

    from archivist import about
    from archivist.archivist import Archivist
    from archivist.parser import common_parser, endpoint

    LOGGER = getLogger(__name__)

    def run(arch: Archivist, args):

        LOGGER.info("Using version %s of jitsuin-archivist", about.__version__)
        LOGGER.info("Namespace %s", args.namespace)

        with open(args.yamlfile, "r", encoding="utf-8") as y:
            arch.runner(parse_config(data=y)

        sys_exit(0)

    def main():
        parser = common_parser("Executes the archivist runner from a yaml file")

        parser.add_argument(
            "yamlfile", help="the yaml file describing the steps to conduct"
        )
        args = parser.parse_args()

        arch = endpoint(args)

        run(arch, args)

        parser.print_help(sys_stdout)
        sys_exit(1)


Command Line
------------

This functionality is also available with the CLI tool :code:`archivist_runner`, which is bundled with version v0.10 onwards of the :code:`jitsuin-archivist`.

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


Example Yaml Snippet
--------------------

This is an example of creating an asset and creating an event for that asset. The
yaml file consists of a list of steps.

Each step consists of control parameters (specified in the 'step' dictionary) and 
the yaml representation of the request body for an asset or event.

The confirm: field is a control variable for the PythonSDK that ensures that the
asset or event is confirmed before returning.

.. note::

   The name of the asset is important. The value of the name is carried forward for
   every operation - in this case the name of the asset is 'radiation bag 1'.

   Arguments to the archivist are usually strings - in this example radioactive is 
   'true' which archivist will treat as a boolean.


.. code:: yaml

    ---
    # Demonstration of applying a Richness compliance policy to an asset that undergoes
    # events that may or may not make the asset compliant or non-compliant.
    #
    # The operation field is a string that represents the method bound to an endpoint and
    # the args and kwargs correspond to the arguments to such a method.
    #
    # NB the assets and events endpoints require all values to be strings. Other values may
    # be of the correct type such as confirm which is a boolean.
    #
    steps:

      # note the values to the assets.create method are string representations of boolean
      # and numbers
      - step:
          action: ASSETS_CREATE
          description: Create an empty radiation bag with id 1.
          asset_label: radiation bag 1
        behaviours:
          - Attachments
          - RecordEvidence
        attributes:
          arc_display_name: radiation bag 1
          radioactive: "true"
          radiation_level: "0"
          weight: "0"
        confirm: true

      # setup the radiation bags to have a varing amount of radiactive waste
      # note the values to the events.create method are string representations of boolean
      # and numbers
      - step:
          action: EVENTS_CREATE
          description: Create Event adding 3 rads of radiation to bag 1, increasing its weight by 1kg.
          asset_label: radiation bag 1
        operation: Record
        behaviour: RecordEvidence
        event_attributes:
          arc_description: add waste to bag
          arc_evidence: see attached conformance report
          conformance_report: blobs/e2a1d16c-03cd-45a1-8cd0-690831df1273
        asset_attributes:
          radiation_level: "3"
          weight: "1"
        confirm: true

Logging
========

Follows the Django model as described here: https://docs.djangoproject.com/en/3.2/topics/logging/

The base logger for this package is rooted at "archivist" with subloggers for each endpoint:

.. note::
    archivist.archivist
        sublogger for archivist submodule

    archivist.assets
        sublogger for assets submodule

and for other endpoints.

Logging is configured by either defining a root logger with suitable handlers, formatters etc. or
by using dictionary configuration as described here: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

A recommended minimum configuration would be:

.. code:: python

    import logging

    logging.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    })

For convenience this has been encapsulated in a convenience function :code:`set_logger`
which should be called before anything else:

.. code:: python

    from archivist.logger import set_logger
    from archivist.archivist import Archivist

    set_logger("DEBUG")
    client_id = getenv("ARCHIVIST_CLIENT_ID")
    client_secret_file = getenv("ARCHIVIST_CLIENT_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    arch = Archivist(
        "https://app.rkvst.io",
        (client_id, client_secret),
        max_time=300,
    )

Development
===========

For instructions on contributing to the RKVST SDK see DEVELOPMENT.md.
