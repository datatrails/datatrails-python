"""Asset data class

"""
from __future__ import annotations


class Asset(dict):
    """Asset

    Asset object has dictionary attributes and properties.

    """

    @property
    def primary_image(self) -> str | None:
        """Primary Image

        Attachment that is the primary image of the asset.

        Returns:
            :class:`Attachment` instance

        """
        try:
            attachments = self["attributes"]["arc_attachments"]
        except (KeyError, TypeError):
            pass
        else:
            return next(  # pragma: no cover
                (
                    a
                    for a in attachments
                    if "arc_display_name" in a
                    if a["arc_display_name"] == "arc_primary_image"
                ),
                None,
            )

        return None

    @property
    def name(self) -> str | None:
        """str: name of the asset"""
        name = None
        try:
            name = self["attributes"]["arc_display_name"]
        except (KeyError, TypeError):
            pass

        return name
