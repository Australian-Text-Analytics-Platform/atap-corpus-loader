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
- include_meta_loader: bool - If True, the Corpus Loader will include additional metadata joining functionality. False by default
- params: Any – passed onto the panel.viewable.Viewer super-class

Example

```python
loader = CorpusLoader('tests/test_data', include_meta_loader=True)
```

---

### CorpusLoader.servable

Inherited from panel.viewable.Viewer. Call CorpusLoader.servable() in a Jupyter notebook context to display the CorpusLoader widget.

Example

```python
loader = CorpusLoader('tests/test_data')
loader.servable()
```

---

### CorpusLoader.add_tab

Allows adding a Panel Viewable instance to the tab controls of the loader.

Params
- new_tab_name: str – The name of the tab that will appear on the tab control bar
- new_tab_panel: Viewable - The pane to attach to the new tab

Example

```python
loader = CorpusLoader('tests/test_data')
loader.add_tab("A Panel Column", panel.Column())
```

---

### CorpusLoader.set_build_callback

Allows a callback function to be set when a corpus has completed building.
When the function is called, the only argument passed will be the built corpus object.

Params
- callback: Callable – the function to call when a corpus has been built

Example

```python
corpus_list = []
loader = CorpusLoader('tests/test_data')
loader.set_build_callback(corpus_list.append)
```

---

### CorpusLoader.get_latest_corpus

Returns: DataFrameCorpus or None - the last DataFrameCorpus object that was built. If none have been built, returns None.

Example

```python
loader = CorpusLoader('tests/test_data')
corpus = loader.get_latest_corpus()
```

---

### CorpusLoader.get_corpus

Params
-  name: str – The name of the DataFrameCorpus to retrieve.

Returns: DataFrameCorpus or None - the DataFrameCorpus object in the corpora with the provided name. If none with the provided name are found, returns None.

Example

```python
loader = CorpusLoader('tests/test_data')
corpus = loader.get_corpus("example")
```

---

### CorpusLoader.get_corpora

Returns: dict[str, DataFrameCorpus] - a dictionary that maps Corpus names to DataFrameCorpus objects that have been built using this CorpusLoader

Example

```python
loader = CorpusLoader('tests/test_data')
corpus_map = loader.get_corpora()
```

---

### CorpusLoader.get_mutable_corpora

Returns the corpora object that contains the loaded corpus objects.
This allows adding to the corpora from outside the CorpusLoader as the object returned is mutable, not a copy.
The Corpora object has a unique name constraint, meaning a corpus object cannot be added to the corpora if another corpus with the same name is already present. The same constraint applies to the rename method of corpus objects added to the corpora.

Returns: TCorpora - the mutable corpora object that contains the loaded corpus objects

Example

```python
loader = CorpusLoader('tests/test_data')
corpora_object = loader.get_mutable_corpora()
corpus = corpora_object.get("example")
```

---

## Example usage

The following snippet could be used as a cell in a Jupyter notebook. Each time the user builds a corpus, the built corpus will be added to the list.

```python
from atap_corpus_loader import CorpusLoader

corpus_list = []
loader = CorpusLoader('tests/test_data')
loader.set_build_callback(corpus_list.append)
loader.servable()
```