# Welcome to pytest-vcr

Plugin for managing [VCR.py](https://vcrpy.readthedocs.io/) cassettes.

**WARNING: None of this is implemented yet, I'm trying to start with docs for the basic functionality I want before actually writing any code**
If you have any comments on what's described here you are welcome to open an Issue here: [https://github.com/ktosiek/pytest-vcr/issues](https://github.com/ktosiek/pytest-vcr/issues)

# Quick Start

Install the plugin with:

```sh
pip install pytest-vcr
```

Annotate your tests:

```python
@pytest.mark.vcr()
def test_iana():
  response = urllib2.urlopen('http://www.iana.org/domains/reserved').read()
  assert 'Example domains' in response
```

And that's it!
A new file `_cassettes/test_iana.yaml` will be created on the first run.
This file should be committed to a VCS, as it's a part of your tests.


# Example configuration

## Filtering saved request/response
VCR.py registers full request and response, including headers.
It's important to make sure you aren't leaving any secrets in your cassettes.
For example, when using HTTP Basic authentication, you'd add this to your conftest:

```python
@pytest.fixture
def vcr_config():
  return {
    # Replace the Authorization request header with "DUMMY" in cassettes
    filter_headers=[('authorization', 'DUMMY')],
  }
```

For a way to specify separate configuration for different tests see [Configuration](configuration.md).


## Changing the cassettes library path
By default pytest-vcr will put cassettes in a `_cassettes` directory next to your tests.
You can change the name in your pytest.ini:

```ini
[pytest]
vcr_directory = vhs
```

or by overriding the `vcr_cassette_path` fixture:

```python
@pytest.fixture
def vcr_cassette_path(request, vcr_cassette_name):
    # Put all cassettes in vhs/{module}/{test}.yaml
    return os.path.join('vhs', request.module.__name__, vcr_cassette_name)
```


# Running on CI
When running your tests on CI it's recommended to use the `--vcr-record-mode=none` option.
This way you can make sure that you have committed all the cassettes.
