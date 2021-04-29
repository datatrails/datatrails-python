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

"""Get all assets from a instance of Archivist

The module contains two functions: main and fetch_all_assets. Main function parses in
a url, which is an instance of Archivist and a token, which is a user authorization.
The main function would then call fetch_all_assets and pass in the two variables and
fetch_all_assets will build a connection to the instance and fetch all assets from
the instances.
"""


from archivist.archivist import Archivist


def main():
    """ Main function of get_asset.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and fetch all assets.
    """
    with open(".auth_token", mode='r') as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://soak-0-avid.engineering-k8s-stage-2.dev.wild.jitsuin.io",
        auth=authtoken,
    )
    for asset in arch.assets.list():
        print("asset id:", asset['identity'])


if __name__ == "__main__":
    main()
