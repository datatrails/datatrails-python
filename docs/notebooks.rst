.. _notebooksref:

Note Books (BETA)
=================

.. note::

   This feature is a Work-In-Progress

These are a collection of jupyter notebooks that demonstrate typical use cases of the DATATRAILS
system.

They can be downloaded and executed on Linux, Mac or Windows machines.

The recommended jupyter environment is the JupyterLab Desktop which is available for Linux, Mac or Windows.

https://github.com/jupyterlab/jupyterlab-desktop

    #. Please install this on your desktop following the instructions described in this link.
        #. When prompted initialize a bundled python environment for JupyterLab Desktop.
    #. Download the Notebooks from the link below and unzip into a suitable folder.
    #. Execute JupyterLab Desktop and select the directory where the downloaded notebooks are located.
    #. Execute the 'Initialization and Credentials' notebook and set your credentials.
    #. Execute selected notebooks.
    #. Create new notebooks.....
   
Download Notebooks
..................

Download the notebooks into a suitable folder:

    #. Recommended to call the folder '~/notebooks'
    #. Restrict access by changing the folder permissions 'chmod 700 ~/notebooks'
    #. On Windows only allow the owner access to this folder. Either use the dialog or the 'icacls' command.


.. only:: builder_html or readthedocs

   See :download:`Notebooks <notebooks/notebooks.zip>`.

.. toctree::
   :maxdepth: 2
   :caption: Preparation of Notebooks Environment

   notebooks/Initialization and Credentials.ipynb

.. toctree::
   :maxdepth: 2
   :caption: Managing Credentials in Notebook Environment

   notebooks/Manage_Credentials

.. toctree::
   :maxdepth: 2
   :caption: Basic Asset and Event Examples

   notebooks/Create Artist and Album Release Info
   notebooks/Find Artist and Additional Album Release Info
   notebooks/Find Artist and Create Cover Art
   notebooks/Create Event with Verified Domain

.. toctree::
   :maxdepth: 2
   :caption: Access Policy Examples

   notebooks/Sharing Artist Asset with User
   notebooks/Sharing Album Release Info with User
   notebooks/Sharing Artist Asset with Record Labels
   notebooks/Sharing Album Release Info with Record Labels
