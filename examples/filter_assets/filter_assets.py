# Copyright 2019-2021 Jitsuin, inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is API SAMPLE CODE, not for production use.

"""Filter assets of a archivist connection given url to Archivist and user Token.

The module contains three functions: main, get_matching_assets and _get_matching_resources.
Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "aconn", then call get_matching_assets and pass in "aconn", properties and
attribtues. "get_matching_assets" filters assets of certain properties and attributes from all
assets and return the filted assets.
"""


from archivist.archivist import Archivist


def main():
    """Main function of filtering assets.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and passed-in properties
    attributes to filter all assets of the selected properties and
    attributes through function get_matching_assets.
    """
    with open(".auth_token", mode="r") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://soak-0-avid.engineering-k8s-stage-2.dev.wild.jitsuin.io",
        auth=authtoken,
    )

    # list all assets with required attributes and properties
    props = {"confirmation_status": "CONFIRMED"}
    attrs = {"arc_display_type": "Traffic light"}

    # iterate through the generator....
    for asset in arch.assets.list(props=props, attrs=attrs):
        print("asset", asset)

    # alternatively one could pull the list and cache locally...
    assets = list(arch.assets.list(props=props, attrs=attrs))
    for asset in assets:
        print("asset", asset)


if __name__ == "__main__":
    main()
