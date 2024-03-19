# atap_corpus_loader Documentation

---

## Docs

### atap_corpus_loader.CorpusLoader.CorpusLoader

Public interface for the CorpusLoader module. Maintains a reference to the logic Controller and the GUI wrapper. A CorpusLoader object can be used as a Panel component, i.e. will render in a Panel GUI. The build_callback_fn will be called when a corpus is built (can be set using set_build_callback()).

Can be imported using:

```python
from atap_corpus_loader import CorpusLoader
```

---

### CorpusLoader.\_\_init\_\_

CorpusLoader constructor

Params
-  root_directory: str – The root directory that the file selector will search for files to load. The argument must be a string. The directory may be non-existent at initialisation time, but no files will be displayed until it exists.
- params: Any – passed onto the panel.viewable.Viewer super-class

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')'
```

---

### CorpusLoader.servable

Inherited from panel.viewable.Viewer. Call CorpusLoader.servable() in a Jupyter notebook context to display the CorpusLoader widget.

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')
loader.servable()
```

---

### CorpusLoader.set_build_callback

Allows a callback function to be set when a corpus has completed building

Params
- callback: Callable – the function to call when a corpus has been built
- args: Any – positional arguments to pass onto the callback function
- kwargs: Any – keyword arguments to pass onto the callback function

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')
loader.set_build_callback(foo(loader))
```

---

### CorpusLoader.get_latest_corpus

Returns: DataFrameCorpus | None - the last DataFrameCorpus object that was built. If none have been built, returns None.

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')
corpus = loader.get_latest_corpus()
```

---

### CorpusLoader.get_corpus

Params
-  name: str – The name of the DataFrameCorpus to retrieve.

Returns: DataFrameCorpus | None - the DataFrameCorpus object in the corpora with the provided name. If none with the provided name are found, returns None.

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')
corpus = loader.get_corpus("example")
```

---

### CorpusLoader.get_corpora

Returns: list[DataFrameCorpus] - a list of DataFrameCorpus objects that have been built using this CorpusLoader

Example

```python
loader = CorpusLoader('atap_corpus_loader_tests/test_data')
corpus_list = loader.get_corpora()
```

---

## Example usage

The following snippet could be used as a cell in a Jupyter notebook. Each time the user builds a corpus, the contents will be printed.

```python
from atap_corpus_loader import CorpusLoader
from pandas import DataFrame

def print_corpus_df(loader: CorpusLoader):
    corpus_df: DataFrame | None = loader.get_latest_corpus()
    if corpus_df is not None:
        print(corpus_df.to_dataframe().to_string())


loader = CorpusLoader('atap_corpus_loader_tests/test_data')
loader.set_build_callback(print_corpus_df, loader)
loader.servable()
```