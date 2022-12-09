.. _notebooksref:

Note Books (BETA)
=================

.. note::

   This feature is a Work-In-Progress

These are a collection of jupyter notebooks that demonstrate typical use cases of the RKVST
system.

They can be downloaded and executed on a Linux, Mac or Windows machines. The only requirement
is that python3.7 to python3.11 and pip command-line too have been installed.

Installing the RKVST python SDK
...............................

The bare requirement is that a version of python3 (3.7 to 3.11) is installed together with
the pip command-line tool.

Linux
~~~~~

Most Linux distros come with a suitable version of python3 already installed. The only extra requirement
is to install the pip command-line utility. 

.. code:: bash

   python3 -m ensurepip --upgrade

MacOS
~~~~~

Python installation instructions for MacOS are `pythonmac installation instructions`_

.. _pythonmac installation instructions: https://www.python.org/downloads/macos/

Open a terminal and ensure that python and pip are available:

.. code:: bash

   python --version
   pip --version

Windows
~~~~~~~

Python installation instructions for Windows are `pythonwindows installation instructions`_

.. _pythonwindows installation instructions: https://www.python.org/downloads/windows/

Execute the installer. Ensure the following:
   
* Installation of pip is enabled
* py launcher is enabled
* Associate file with python is enabled
* Create shortcuts for installed applications
* Add Python to Path

Open a 'cmd' terminal and ensure that python and pip are available:

.. code:: bash

   python --version
   pip --version
   
Download Notebooks
..................

.. only:: builder_html or readthedocs

   See :download:`Notebooks <notebooks/notebooks.zip>`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :name: Gallery

   notebooks/Manage_Credentials
   notebooks/Check Asset Compliance using CURRENT OUTSTANDING Policy
   notebooks/Check Asset Compliance using SINCE Policy
   notebooks/Create Event with Verified Domain
   notebooks/Share_Asset
   

