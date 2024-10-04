# atap_corpus_loader Documentation

---

## Docs

### atap_corpus_loader.CorpusLoader

Public interface for the CorpusLoader module. Maintains a reference to the logic Controller and the GUI wrapper. A CorpusLoader object can be used as a Panel component, i.e. will render in a Panel GUI. Callbacks can be registered using the register_event_callback() method

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
- include_oni_loader: bool - If True, the Corpus Loader will include additional Oni integration functionality. False by default
- run_logger: bool - If True, a log will be kept in the atap_corpus_loader directory. False by default
- params: Any – passed onto the panel.viewable.Viewer super-class

Example

```python
loader = CorpusLoader('tests/test_data', include_meta_loader=True, include_oni_loader=True, run_logger=True)
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

### CorpusLoader.register_event_callback

Registers a callback function to execute when the event specified by event_type occurs.
Multiple callback functions can be registered and will be called in the order added when the event occurs.
If the first argument is True, the callback will be added to the start of the callback chain rather than the end.
Subsequent callbacks registered with first=True will supersede the previous callback's position.
When a callback raises an exception, the exception will be logged and the subsequent callbacks will be executed.
The relevant corpus object will be passed as an argument for the BUILD and RENAME events.
A list of added corpus objects will be passed as an argument for the IMPORT event.

Params
- event_type: EventType or str - an enum with the possible values: LOAD, UNLOAD, BUILD, IMPORT, RENAME, DELETE. String equivalents also accepted
- callback: Callable - the function to call when the event occurs
- first: bool - whether to insert the callback at the start of the callback chain for this event type. False by default

Example

```python
corpus_list = []
loader = CorpusLoader('tests/test_data')
loader.register_event_callback(EventType.BUILD, corpus_list.append)
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

### CorpusLoader.get_logs

Returns the log history as read from the log file as a string.
If the log file is inaccessible, returns empty string.

Returns: str - the recent log history as read from the log file

Example

```python
loader = CorpusLoader('tests/test_data', run_logger=True)
log_str = loader.get_logs()
```

---

## Notes

### Document Term Matrix

When a corpus is built using the CorpusLoader, a Term Frequency Document Term Matrix (DTM) is added to the corpus. The key used for this DTM is 'tokens'. Consult the atap_corpus documentation for further details

### Callbacks

Callback functions can be registered with CorpusLoader.register_event_callback(), which registers a callback function to execute when the event specified by event_type occurs.
Multiple callback functions can be registered and all will be called in order when the event occurs.
When a callback raises an exception, the exception will be logged and the subsequent callbacks will be executed.
The relevant corpus object will be passed as an argument for the BUILD and RENAME events. The other event callbacks will pass no arguments.

The EventType enum can be imported using:

```python
from atap_corpus_loader import EventType
```

## Example usage

The following snippet could be used as a cell in a Jupyter notebook. Each time the user builds a corpus, the built corpus will be added to the list.

```python
from atap_corpus_loader import CorpusLoader, EventType

corpus_list = []
loader = CorpusLoader('tests/test_data')
loader.register_event_callback(EventType.BUILD, corpus_list.append)
loader.servable()
```