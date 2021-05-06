# Jitsuin Archivist Client Development

## Pre-requisites

Required tools for this repo are task-runner and docker-ce.

Install task runner: https://github.com/go-task/task
Install docker-ce: https://docs.docker.com/get-docker/

## Workflow

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

Make a change to the code and validate the changes:

```bash
task check
```

If ok run the unittests:

```bash
task unittests
```

If 100% coverage and no test failures generate the wheel:

```bash
task wheel
```

Lastly to publish the package to PyPi:

```bash
task publish
```

Note that this requires credentials and will only normally be done by a Jitsuin
representative.


## Testing Other Python Versions

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