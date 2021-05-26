# Jitsuin Archivist Client

The standard Jitsuin Archivist python client.

Please note that the canonical API for Jitsuin Archivist is always the REST API
documented at https://jitsuin-archivist.readthedocs.io

# Installation

Use standard python pip utility:

```bash
python3 -m pip install jitsuin-archivist
```

One can then use the examples code to create assets:

```python
from archivist.archivist import Archivist
from archivist.errors import ArchivistError

# Oauth2 token that grants access
with open(".auth_token", mode='r') as tokenfile:
    authtoken = tokenfile.read().strip()

# Initialize connection to Archivist - the URL for production will be different to this URL
arch = Archivist(
    "https://rkvst.poc.jitsuin.io",
    auth=authtoken,
)

# Create a new asset
attrs = {
    "arc_display_name": "display_name",  # Asset's display name in the user interface
    "arc_description": "display_description",  # Asset's description in the user interface
    "arc_display_type": "desplay_type",  # Arc_display_type is a free text field
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
behaviours = ["Attachments", "Firmware", "LocationUpdate", "Maintenance", "RecordEvidence"]

# The first argument is the behaviours of the asset
# The second argument is the attributes of the asset
# The third argument is wait for confirmation:
#   If @confirm@ is True then this function will not
#   return until the asset is confirmed on the blockchain and ready
#   to accept events (or an error occurs)
#   After an asset is submitted to the blockchain (submitted),
#   it will be in the "Pending" status.
#   Once it is added to the blockchain, the status will be changed to "Confirmed"
try:
    asset = arch.assets.create(behaviours, attrs=attrs, confirm=True)
except Archivisterror as ex:
    print("error", ex)
else:
    print("asset", asset)

```

# Development

See BUILDING.md

