# Hacking

## Documentation
When working on documentation it's handy to run `tox -e mkdocs -- serve`.
This will start a server on 127.0.0.1:8000 that shows the rendered documentation.

## Code
To run all tests and checks just use `tox`.

## Test coverage
When running tests by `tox`, test coverage is collected in the parallel mode.
To see combined results across all the environments run `coverage combine && coverage html`.
