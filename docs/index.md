# Welcome to pytest-vcr


Py.test plugin for managing [VCR.py](https://vcrpy.readthedocs.io/) cassettes.


# Quick Start

Install the plugin:

```sh
pip install pytest-vcr
```

Annotate your tests:

```python
@pytest.mark.vcr()
def test_iana():
    response = urlopen('http://www.iana.org/domains/reserved').read()
    assert b'Example domains' in response
```

And that's it!
A new file `cassettes/test_iana.yaml` will be created next to your test file on the first run.
This file should be committed to a VCS.


# Example configuration

## Filtering saved request/response
VCR.py registers full request and response, including headers, which often include passwords or API keys.
It's important to make sure you aren't leaving any secrets in your cassettes.
For example, when using HTTP Basic authentication, you should add this to your conftest:

```python
@pytest.fixture
def vcr_config():
    return {
        # Replace the Authorization request header with "DUMMY" in cassettes
        filter_headers: [('authorization', 'DUMMY')],
    }
```

For a way to specify separate configuration for different tests see [Configuration](configuration.md).


## Changing the cassettes library path
By default pytest-vcr will put cassettes in a `cassettes` directory next to your tests.
You can change that by overriding the `vcr_cassette_path` fixture:

```python
@pytest.fixture
def vcr_cassette_path(request, vcr_cassette_name):
    # Put all cassettes in vhs/{module}/{test}.yaml
    return os.path.join('vhs', request.module.__name__, vcr_cassette_name)
```


# Running on CI
When running your tests on CI it's recommended to use the `--vcr-record=none` option.
This way you can make sure that you have committed all the cassettes.
