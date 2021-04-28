"""assets interface

   Wrap base methods with constants for assets (path, etc...
"""

from copy import deepcopy
from time import sleep

from .constants import (
    ASSETS_SUBPATH,
    ASSETS_LABEL,
    CONFIRMATION_CONFIRMED,
    CONFIRMATION_FAILED,
    CONFIRMATION_STATUS,
    CONFIRMATION_PENDING,
)
from .errors import ArchivistUnconfirmedError
from .logger import LOGGER

DEFAULT_PAGE_SIZE=500


class _AssetsClient:
    """docstring
    """
    backoff = 1.0
    timeout = 1200

    def __init__(self, archivist):
        """docstring
        """
        self._archivist = archivist

    def create(self, behaviours, attrs, confirm=False):
        """docstring
        """
        return self.create_from_data(
            {
                'behaviours': behaviours,
                'attributes': attrs,
            },
            confirm=confirm,
        )

    def create_from_data(self, data, confirm=False):
        """docstring

        read request from data stream
        suitable for reading data from a file using json.load or yaml.load
        """
        asset = Asset(**self._archivist.post(
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
            data,
        ))
        if not confirm:
            return asset

        return self.wait_for_confirmation(asset['identity'])

    def wait_for_confirmation(self, identity):
        """docstring
        """
        backoff = self.backoff
        timeout = self.timeout

        while timeout > 0:
            timeout -= backoff
            asset = self.read(identity)

            if CONFIRMATION_STATUS not in asset:
                raise ArchivistUnconfirmedError(
                    f"cannot confirm {identity} as confirmation_status is not present"
                )

            if asset[CONFIRMATION_STATUS] == CONFIRMATION_FAILED:
                raise ArchivistUnconfirmedError(
                    f"confirmation for {identity} FAILED - this is unusable"
                )

            if asset[CONFIRMATION_STATUS] != CONFIRMATION_CONFIRMED:
                sleep(backoff)
                backoff += backoff * 0.25
            else:
                return asset

        raise ArchivistUnconfirmedError(
            f"confirmation for {identity} timed out after {self.timeout} seconds"
        )

    def read(self, identity):
        """docstring
        """
        return Asset(**self._archivist.get(ASSETS_SUBPATH, identity))

    @staticmethod
    def __query(props, attrs):
        """docstring
        """
        query = deepcopy(props) if props else {}
        if attrs:
            query['attributes'] = attrs

        return query

    def count(self, *, props=None, attrs=None):
        """docstring
        """
        return self._archivist.count(
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
            query=self.__query(props, attrs)
        )

    def wait_for_confirmed(self, *, props=None, attrs=None):
        """docstring
        """
        backoff = self.backoff
        timeout = self.timeout

        newprops = deepcopy(props) if props else {}
        newprops[CONFIRMATION_STATUS] = CONFIRMATION_PENDING

        while timeout > 0:
            timeout -= backoff
            LOGGER.debug("Count unconfirmed assets %s, %s", newprops, attrs)
            count = self.count(props=newprops, attrs=attrs)

            if count == 0:
                # did any fail
                newprops = deepcopy(props) if props else {}
                newprops[CONFIRMATION_STATUS] = CONFIRMATION_FAILED
                count = self.count(props=newprops, attrs=attrs)
                if count > 0:
                    raise ArchivistUnconfirmedError(f"There are {count} FAILED assets")

                return

            sleep(backoff)
            backoff += backoff * 0.25

        raise ArchivistUnconfirmedError(
            f"{count} pending assets still present after {self.timeout} seconds"
        )

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, props=None, attrs=None):
        """docstring
        """
        return (
            Asset(**a) for a in self._archivist.list(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                page_size=page_size,
                query=self.__query(props, attrs)
            )
        )

    def read_by_signature(self, *, props=None, attrs=None):
        """docstring
        """
        return Asset(**self._archivist.get_by_signature(
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
            ASSETS_LABEL,
            query=self.__query(props, attrs)
        ))


class Asset(dict):
    """docstring
    """
    @property
    def primary_image(self):
        """docstring
        """
        try:
            attachments = self['attributes']['arc_attachments']
        except (KeyError, TypeError):
            pass
        else:
            return next(  # pragma: no cover
                (a for a in attachments
                    if 'arc_display_name' in a
                    if a['arc_display_name'] == "arc_primary_image"),
                None
            )

        return None

    @property
    def name(self):
        """docstring
        """
        try:
            name = self['attributes']['arc_display_name']
        except (KeyError, TypeError):
            pass
        else:
            return name

        return None
