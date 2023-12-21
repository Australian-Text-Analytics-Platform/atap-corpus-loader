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
- rds
- RData/RDa

## Setup

### Prerequisites

- [Python 3.10](https://www.python.org/)

Run the following commands in a terminal or any Bash environment.

Clone the repository and navigate into the newly created directory:

```shell
git clone https://github.com/Australian-Text-Analytics-Platform/atap_corpus_loader.git
cd atap_corpus_loader
```

To install dependencies, ensure you have Python 3.10 and pip installed, then run the following command:

```shell
python -m pip install -r requirements.txt
```

Serve the application locally using the following command:

```shell
panel serve corpusloader.ipynb
```

The application will be usable in a browser at the link provided (http://localhost:5006/corpusloader)

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Australian-Text-Analytics-Platform/atap_corpus_loader/tags).

## Authors

  - **Hamish Croser** - [h-croser](https://github.com/h-croser)

## License

This project is licensed under the [The MIT License](LICENSE)
The MIT License - see the [LICENSE](LICENSE) file for details
