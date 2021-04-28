# Jitsuin Archivist Client

The standard Jitsuin Archivist python client

# Development Workflow

To see what is available simply execute:

```bash
task
```

To builde the docekr builder image:
```bash
task builder
```

Make a change to the code and execute:

```bash
task check
```

to validate the code.

If ok run the unittests:

```bash
task unittests
```

If 100% coverage and no test failures generate the wheel:

```bash
task wheel
```
