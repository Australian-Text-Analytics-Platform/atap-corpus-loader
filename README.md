# Corpus Loader

A GUI loader for atap_corpus using the Panel library. Provides a single Panel-compatible widget in which a user can construct a corpus object for use by the client code.

### File Type support

The loader currently supports loading a corpus from the following file types:
- txt
- odt
- docx
- csv
- tsv
- xlsx
- ods
- xml

## Installation

```shell
python3 -m pip install atap-corpus-loader
```

## Documentation

Documentation can be found [here](https://australian-text-analytics-platform.github.io/atap-corpus-loader/DOCS.html)

## Tests

```shell
python3 tests/tests.py
```

## Contributing

The package for this project is hosted on PyPi: https://pypi.org/project/atap-corpus-loader/

Dependencies, publishing, and version numbering is handled by [Poetry](https://python-poetry.org)

To publish a new version:

```shell
poetry config pypi-token.pypi <TOKEN>
poetry version minor
poetry build
poetry publish
```

## Authors

  - **Hamish Croser** - [h-croser](https://github.com/h-croser)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
