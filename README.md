# Corpus Loader

> [!WARNING]
> **This tool is archived and no longer supported or maintained.**
> It was developed by the Australian Text Analytics Platform (ATAP), the previous phase of the
> Language Data Commons of Australia (LDaCA). It is preserved as a frozen Docker image so that it
> keeps launching on BinderHub as it last worked, but it will not be updated or fixed.
> For current LDaCA text analytics tools, please use
> [Wordflow](https://australian-text-analytics-platform.github.io/LDaCa_Text_Analytics_Tools/) and
> [LADAL](https://ladal.edu.au).

## Launch on Binder

[![Binder](https://binderhub.rc.nectar.org.au/badge_logo.svg)](https://binderhub.rc.nectar.org.au/v2/gh/Australian-Text-Analytics-Platform/atap-corpus-loader/archived?labpath=corpusloader.ipynb)

<b>Note:</b> Australian Access Federation (AAF) or Reannz Tuakiri (NZ) authentication is required.
If you do not have access to AAF or NZ, you can use the below link to access the tool (this is a free Binder version, limited to 2GB memory only).

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Australian-Text-Analytics-Platform/atap-corpus-loader/archived?labpath=corpusloader.ipynb)

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

## Run locally with Docker

The frozen environment of this tool is published as the Docker image
[`milysun/atap-atap-corpus-loader`](https://hub.docker.com/r/milysun/atap-atap-corpus-loader). With [Docker](https://docs.docker.com/get-docker/) installed, run:

```bash
docker run --rm -p 8888:8888 milysun/atap-atap-corpus-loader:c45451e2494b jupyter lab --ip=0.0.0.0 --port=8888
```

then open the `http://127.0.0.1:8888/lab?token=...` link printed in the terminal.
On Apple Silicon Macs add `--platform linux/amd64` after `docker run`.
