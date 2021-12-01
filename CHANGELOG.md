# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Python 3.9 support

### Removed

- Title and description roles
- Support for albums in image directive
- `imgur_target_default_gallery` and `target_gallery` options
- Caching and querying Imgur's API
- Auto-detecting size, extension/type, and album images
- Dropped Python 2.7 and <3.6 support
- Imgur ID checks (no more babysitting users)

### Fixed

- Support for Sphinx 1.8

### Changed

- Renamed project from `sphinxcontrib-imgur` to `sphinx-imgur`
- Re-licensed from MIT to BSD 2-Clause

## [2.0.1] - 2016-10-15

### Changed

- Adding newlines after imgur-image image/a HTML tags. Without those newlines Chrome doesn't display gaps between images on
  the same line.

## [2.0.0] - 2016-10-15

### Added

- Python 3.5 support (Linux/OS X and Windows).
- `imgur-image` directive.
- `imgur_target_default_gallery`, `imgur_target_default_largest`, and `imgur_target_default_page` conf variables.

### Changed

- Rewrote most of the library. Previous code was ugly, complicated, and hard to follow.

### Removed

- PyPy support.
- `imgur_api_test_response` conf variable.

## [1.0.0] - 2015-08-09

### Added

- Initial release.
