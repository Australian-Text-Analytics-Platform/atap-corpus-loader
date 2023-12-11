from panel import Row, Spacer, Column, HSpacer, bind
from panel.widgets import Button, TextInput

from corpusloader.controller import Controller
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.FileSelectorWidget import FileSelectorWidget
from corpusloader.view.gui.MetaEditorWidget import MetaEditorWidget


class FileLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: AbstractWidget, controller: Controller, base_path: str):
        super().__init__()
        self.view_handler: AbstractWidget = view_handler
        self.controller: Controller = controller
        self.directory: str = base_path
        
        self.load_as_corpus_button: Button = Button(name='Load as corpus', width=130,
                                                    button_style='solid', button_type='success')
        self.load_as_corpus_button.on_click(self.load_as_corpus)
        self.load_as_meta_button: Button = Button(name='Load as metadata', width=130,
                                                  button_style='solid', button_type='success')
        self.load_as_meta_button.on_click(self.load_as_meta)
        self.unload_button: Button = Button(name="Unload all", width=100, button_style='solid',
                                            button_type='danger', disabled=True)
        unload_fn = bind(self._set_build_buttons_status, False)
        self.unload_button.on_click(unload_fn)
        
        self.corpus_name_input = TextInput(placeholder='Corpus name', width=150, visible=False)
        self.build_button = Button(name='Build corpus', button_style='solid', button_type='success', visible=False)
        self.build_button.on_click(self.build_corpus)

        self.file_selector = FileSelectorWidget(view_handler, controller, base_path)
        self.meta_editor = MetaEditorWidget(view_handler, controller)

        self.panel = Row(
            Column(
                self.file_selector,
                Row(self.load_as_corpus_button,
                    self.load_as_meta_button,
                    HSpacer(),
                    self.corpus_name_input,
                    self.build_button,
                    width=700),
                Row(self.unload_button)
            ),
            Spacer(width=50),
            self.meta_editor)
        self.children = [self.file_selector, self.meta_editor]

    def update_display(self):
        pass

    def _set_build_buttons_status(self, active: bool, *_):
        if active:
            self.corpus_name_input.visible = True
            self.build_button.visible = True
            self.unload_button.disabled = False
        else:
            self.corpus_name_input.visible = False
            self.build_button.visible = False
            self.unload_button.disabled = True
        self.view_handler.update_displays()

    def load_as_corpus(self, *_):
        file_ls: list[str] = self.file_selector.get_selector_value()
        success = self.controller.load_corpus_from_filepaths(file_ls)
        if success:
            self._set_build_buttons_status(True)
        self.view_handler.update_displays()

    def load_as_meta(self, *_):
        file_ls: list[str] = self.file_selector.get_selector_value()
        success = self.controller.load_meta_from_filepaths(file_ls)
        if success:
            self._set_build_buttons_status(True)
        self.view_handler.update_displays()

    def build_corpus(self, *_):
        pass
