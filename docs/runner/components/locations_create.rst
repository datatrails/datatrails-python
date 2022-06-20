.. _locations_create_yamlref:

Locations Create Story Runner YAML
...........................................

Creates a location and stores a reference in runner variable :code:`location_label`.

.. code-block:: yaml
    
    ---
    steps:
      - step:
          action: LOCATIONS_CREATE_IF_NOT_EXISTS
          description: Create Cape Town Location
        selector:
          - display_name
          - attributes:
            - namespace
        display_name: Cape Town
        description: South Africa Office
        latitude: -33.92527778
        longitude: 18.42388889
        attributes:
          namespace: synsation industries
          address: Cape Town Downtown
          Facility Type: Satellite Office
          reception_email: reception_CT@synsation.io
          reception_phone: +27 (21) 123-456
