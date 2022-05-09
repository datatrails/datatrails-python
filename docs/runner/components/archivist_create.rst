.. _archivist_create_yamlref:

Archivist Create Story Runner YAML
.......................................

This action must be defined as the first action in any runner story. There can be more than one
for different tenants. (typically when sharing assets between tenants...)

:code:`archivist_label` is required and is used to access the endpoint for all other actions.

:code:`url` is required.

Usually these field values are derived from an environment variable 
:code:`ARCHIVIST_NAMESPACE` (default value is :code:`namespace`).

If optional :code:`auth_token` is defined then :code:`client_id` and :code:`client_secret` are not required.

Conversely if :code:`auth_token` is not defined then both :code:`client_id` and :code:`client_secret` must
be specified.

The code:`max_time` and :code:`verify` are optional. If unspecified suitable defaults are used.


With auth_token:

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ARCHIVIST_CREATE
          description: Archivist interface for Acme Corporation
          archivist_label: Acme Corporation
        url: https://app.rkvst.io
        auth_token: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        max_time: 30
        verify: True


With app registration id and secret and default max_time/verify

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: ARCHIVIST_CREATE
          description: Archivist interface for Acme Corporation
          archivist_label: Acme Corporation
        url: https://app.rkvst.io
        client_id: xxxxxxxxxxxxxxxxxxx
        client_secret: yyyyyyyyyyyyyyyyyyyyyyy

