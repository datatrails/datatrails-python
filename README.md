# Jitsuin Archivist Client

The standard Jitsuin Archivist python client.

Please note that the canonical API for Jitsuin Archivist is always the REST API
documented at https://jitsuin-archivist.readthedocs.io

# Installation

Use standard python pip utility:

```bash
python3 -m pip install jitsuin-archivist
```

One can then use the examples code to create assets (see examples directory):

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
behaviours = ["Attachments", "RecordEvidence"]

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

## Logging

Follows the Django model as described here: https://docs.djangoproject.com/en/3.2/topics/logging/

The base logger for this pacakage is rooted at "archivist" with subloggers for each endpoint:

- "archivist.archivist"
- "archivist.assets"
- ...

etc. etc.

Logging is configured by either defining a root logger with suitable handlers, formatters etc. or
by using dictionary configuration as described here: https://docs.python.org/3/library/logging.config.html#logging-config-dictschema

A recommended minimum configuration would be:

```python
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
```

# Development

## Pre-requisites

Required tools for this repo are task-runner and docker-ce.

   - Install task runner: https://github.com/go-task/task
   - Install docker-ce: https://docs.docker.com/get-docker/

## Workflow

### Preparation

Reference: https://gist.github.com/Chaser324/ce0505fbed06b947d962

Fork the repo using the 'Fork' dialog at the top right corner of the github UI.

Clone the new fork into your local development environment (assuming your github
login is 'githubUserHandle'):

> Note: all references to 'git@github.com' assume that your local github user has adequate
> rights. If using ~/.ssh/config to manage ssh identities then replace all mentions of
> 'git@github.com' with the clause name in ~/.ssh/config which references the appropriate
> ssh key::
> 
> For example:
```
Host ssh-githubUserHandle
    User git
    Hostname github.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_githubUserHandle

Host ssh-otherUserHandle
    User git
    Hostname github.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_otherUserHandle

Host *
    IdentitiesOnly yes

```
> i.e. 'githubUserHandle' viz:
>
>    git clone ssh-githubUserHandle:githubUserHandle/archivist-python.git
>


```bash
mkdir githubUserHandle
cd githubUserHandle
git clone ssh-githubUserHandle:githubUserHandle/archivist-python.git
```

Enter the new cloned fork and add the original upstream repo as a remote:

```bash
cd archivist-python
git remote add upstream ssh-githubUserHandle:jitsuin-inc/archivist-python.git
git remote -v
```

Now add a branch for your proposed changes:

```bash
git status
git checkout -b dev/githubUserHandle/some-proposed-fix
git status
```
To see what options are available simply execute:

```bash
task
```

All development is done using a docker image. To create the image execute
the following command. This command only has to be repeated if requirements.txt
or requirements-dev.txt change.

Dependencies are defined in requirements.txt for the archivist package and
requirements-dev.txt for the tools used to build, test and publish the
archivist package.

To build the docker builder image:
```bash
task builder
```
Generate documentation:

```bash
task docs
```

and point a browser to docs/_build/html/index.html.

### Making changes

Make a change to the code and validate the changes:

```bash
task check
```

If ok run the unittests:

```bash
task unittests
```

If you have access to an archivist instance then one can run functional tests. The URL
and authtoken are required. The authtoken must be stored in a file in the credentials
subdirectory credentials/authtoken (say).

These tests will create artefacts on the archivist instance so it is **not** recommended that 
they be run in a production environment.

Set 2 environment variables and execute:

```bash
export TEST_ARCHIVIST="https://rkvst.poc.jitsuin.io"
export TEST_AUTHTOKEN=credentials/authtoken
task functests
```

#### Testing Other Python Versions

##### Python 3.6

To build the docker builder image with default Python version 3.6:
```bash
task builder
```

To check the style
```bash
task check
```

To run the unittests:
```bash
task unittests
```

##### Python 3.7

To build the docker builder image with Python 3.7:
```bash
task builder-3.7
```

To check the style
```bash
task check
```

To run the unittests:
```bash
task unittests
```

##### Python 3.8

To build the docker builder image with Python 3.7:
```bash
task builder-3.8
```

To check the style
```bash
task check
```

To run the unittests:
```bash
task unittests
```

##### Python 3.9

To build the docker builder image with Python 3.9:
```bash
task builder-3.9
```

To check the style
```bash
task check
```

To run the unittests:
```bash
task unittests
```

### Seeking a review

#### Synchronizing the upstream

Bring in latest changes from upstream:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout dev/githubUserHandle/some-proposed-fix
git rebase -i --autosquash main
```

Ensure that your email and name are correct:

```bash
git config user.name
git config user.email
```

#### Pushing changes upstream

Add all changes to a commit using the **example-commit** file as a template
for the commit message.

```bash
git add .
git commit
```

Push the changes upstream(the set-upstream option is only required the first time this is executed):

```bash
git push --set-upstream origin dev/githubUserHandle/some-proposed-fix
```

Enter the github ui at https://github.com/jitsuin-inc/archivist-python and 
generate a pull request.

Reviewers will be notified when a PR is generated and you will receive feedback.
Reviewers will trigger QC checks on your code. Failure will result in
automatic rejection.

#### Making further changes

If changes are requested push the changes as a fixup:

```bash
git add .
git commit --fixup HEAD
git push
```

#### Removing Fixups After Reviewer Approval

Eventually the reviewer(s) will approve your changes. At this point you must
squash all your fixups after syncing upstream:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout dev/githubUserHandle/some-proposed-fix
git rebase -i --autosquash main
git push -f
```

#### PR is merged.

The reviewer will then merge your PR into main.

At this point one must tidy up the local fork:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git log
git branch -d dev/githubUserHandle/some-proposed-fix
```

