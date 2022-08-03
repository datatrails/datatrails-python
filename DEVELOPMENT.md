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

### Development flow

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
export TEST_ARCHIVIST="https://app.rkvst.io"
export TEST_AUTHTOKEN_FILENAME=credentials/authtoken
task functests
```

NOTE: For the access policy functional tests, two separate tenancy tokens are needed for successful test execution.
      Therefore add a another env variable for the second tenancy's auth token:

```
export TEST_AUTHTOKEN_FILENAME_2=credentials/authtoken_tenant_2
```

Alternatively one can use a direct environment variable for the authtoken:
```bash
export TEST_AUTHTOKEN_FILENAME=
export TEST_AUTHTOKEN="ey.....==="
task functests
```

Alternatively one can use a client id and secret obtained from the appregistrations endpoint:
```bash
export TEST_AUTHTOKEN_FILENAME=
export TEST_AUTHTOKEN=
export TEST_CLIENT_ID=c5db8230-6e1c-4b80-9481-d70e647c0429
export TEST_CLIENT_SECRET_FILENAME=credentials/client_secret
task functests
```

Additionally one set the appregistration directly in the environment:

```bash
export TEST_AUTHTOKEN_FILENAME=
export TEST_AUTHTOKEN=
export TEST_CLIENT_ID=c5db8230-6e1c-4b80-9481-d70e647c0429
export TEST_CLIENT_SECRET_FILENAME=
export TEST_CLIENT_SECRET="ey.....................ab=="
task functests
```
When running the runner tests one can specify a namespace to isolate instances of assets in differnt 
runs:
```bash
export ARCHIVIST_NAMESPACE=${RANDOM}
FUNCTEST=execrunner task functests
```

Additional environment variables:

For testing sharing via an access policy requires a second auth token:

```bash
TEST_AUTHTOKEN_FILENAME_2=
```

Testing of the client token refresh logic can take 10 to 20 minutes to complete.
To enable this test set:

```bash
TEST_REFRESH_TOKEN=anything
```

#### Testing Other Python Versions

##### Python 3.7 (default)

To build the docker builder image with default Python 3.7:
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

##### Python 3.8

To build the docker builder image with Python 3.8:
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

##### Python 3.10

To build the docker builder image with Python 3.10:
```bash
task builder-3.10
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

#### Some notes on adding a new endpoint

Adding a new endpoint will involve the following steps:

(for a new endpoint called widgets...)

- edit archivist/constants.py
- add archivist/widgets.py
- add archivist/widget.py
- edit archivist/runner.py
- add unittests/testwidget.py
- add unittests/testwidgets.py
- add functests/execwidgets.py
- add functests/test_resources/widgets_story.yaml
- edit functests/execrunner.py
- add examples/create_widget.py # and other examples as well
- add notebooks/'Create Widgets....ipynb' # and other examples
- add docs/create_widgets.rst
- edit docs/index.rst
- edit docs/getting_started.rst
- add docs/runner/components/widgets.rst
- edit docs/runner/components/index.rst
- add docs/runner/demos/widgets.rst
- edit docs/runner/demos/index.rst


