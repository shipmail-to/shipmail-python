# Contributing

Thanks for helping improve the Shipmail Python SDK.

This repository is published from Shipmail's main codebase, where the SDK is developed and tested
together with the API. Each release replaces the package files here with that source.

- **Issues** are tracked here. Include the package version and a minimal example.
- **Pull requests** are welcome. A maintainer applies an accepted change to the main codebase,
  and it appears here with the next release. The pull request is then closed with a link to that
  release.
- **Security issues**: please follow [SECURITY.md](SECURITY.md) instead of opening an issue.

## Development

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest tests/
```
