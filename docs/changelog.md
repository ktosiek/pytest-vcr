# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2019-04-26
### Fixed
- Mark vcr_config as module scoped in the documentation - by [Bill Ryder](https://github.com/bryder).
- Fix generating the cassette name for unittest.TestCase - by [Arthur Hamon](https://github.com/arthurHamon2).

## [1.0.1] - 2018-11-16
### Fixed
- Only show a deprecation warning for `--vcr-record-mode`, and not for `--vcr-record` - by [Andy Freeland](https://github.com/rouge8).

## [1.0.0] - 2018-11-12
Contributors to this release:
- [Marting Valgur](https://github.com/valgur), who made most of the changes in this release.
- [Andy Freeland](https://github.com/rouge8) adapted the marker usage to pytest 3.6+.

### Added
- `--disable-vcr` option for disabling recording and replay.
- `vcr_cassette_dir` fixture for setting cassette_library_dir.

### Changed
- `vcr` is module scoped now, which helps with using it in fixtures.
- Only the marker closest to the test will be used for configuring VCR.

### Deprecated
- `--vcr-record-mode` is now called `--vcr-record`, the old name is depracated.

### Removed
- `vcr_cassette_path` fixture was removed - use `vcr_cassette_dir` and `vcr_cassette_name` to set the path.
- Support for Python 3.3 was removed.

## [0.3.0] - 2017-05-26
### Added
- `vcr` fixture exposing the `VCR` object.

## [0.2.1] - 2017-05-07
### Changed
- README in ReST format, to help with rendering on pypi.

## [0.2.0] - 2017-05-07
### Changed
- Use separate cassettes for each set of test parametes.
- Change the cassettes directory from `_cassettes` to `cassettes`.
