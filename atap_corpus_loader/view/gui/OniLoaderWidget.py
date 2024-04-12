from panel import Row, Column
from panel.widgets import Select, TextInput, Button, PasswordInput

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view import ViewWrapperWidget
from atap_corpus_loader.view.gui import AbstractWidget


class OniLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget, controller: Controller):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler
        self.controller: Controller = controller

        self.provider_selector = Select(name='Provider selector', width=150)
        self.provider_selector.param.watch(self._on_provider_change, ['value'])

        self.toggle_add_provider_button = Button(name='Add new provider', button_type='primary', button_style='outline')
        self.toggle_add_provider_button.on_click(self._toggle_show_add_provider_pane)

        self.add_provider_name_input = TextInput(name='Provider name', placeholder='Provider name, e.g. MyProvider', visible=False)
        self.add_provider_address_input = TextInput(name='Provider address', placeholder='Provider address, e.g. https://data.atap.edu.au', visible=False)
        self.add_provider_button = Button(name='Add', button_type='success', button_style='solid', visible=False)
        self.add_provider_button.on_click(self._add_provider)
        self.add_provider_panel: Column = Column(self.add_provider_name_input,
                                                 self.add_provider_address_input,
                                                 self.add_provider_button,
                                                 visible=False)

        self.api_key_input = PasswordInput(name='API Key', placeholder='API Key, e.g. af6391e0-f873-11ee-8355-bae397411a92')
        self.api_key_input.param.watch(self._set_api_key, ['value'])

        self.collection_id_input = TextInput(name='Collection ID', placeholder='Collection ID, e.g. arcp://name,corpus-of-oz-early-english')
        self.retrieve_collection_button = Button(name='Retrieve collection', button_type='success', button_style='solid', align='end')
        self.retrieve_collection_button.on_click(self._retrieve_collection)

        self.panel = Column(
            Row(self.provider_selector, align='start'),
            Row(self.toggle_add_provider_button,
                self.add_provider_panel,
                align='start'),
            Row(
                self.api_key_input,
                align='start'
                ),
            Row(self.collection_id_input,
                self.retrieve_collection_button,
                align='center'),
            Row(self.controller.get_build_progress_bar()),
            sizing_mode='stretch_width'
        )
        self.update_display()

    def update_display(self):
        provider_options: list[str] = self.controller.get_providers()
        curr_provider: str = self.controller.get_curr_provider()
        self.provider_selector.options = provider_options
        self.provider_selector.value = curr_provider

    def _on_provider_change(self, *_):
        self.controller.set_curr_provider(self.provider_selector.value)

    def _toggle_show_add_provider_pane(self, *_):
        add_provider_style = self.toggle_add_provider_button.button_style
        if add_provider_style == 'outline':
            self.toggle_add_provider_button.button_style = 'solid'
        elif add_provider_style == 'solid':
            self.toggle_add_provider_button.button_style = 'outline'

        self.add_provider_panel.visible = not self.add_provider_panel.visible
        self.add_provider_name_input.visible = not self.add_provider_name_input.visible
        self.add_provider_address_input.visible = not self.add_provider_address_input.visible
        self.add_provider_button.visible = not self.add_provider_button.visible

    def _add_provider(self, *_):
        provider_name: str = self.add_provider_name_input.value
        provider_address: str = self.add_provider_address_input.value
        self.controller.set_provider(provider_name, provider_address)
        self.add_provider_name_input.value = ''
        self.add_provider_address_input.value = ''
        self._toggle_show_add_provider_pane()
        self.provider_selector.value = provider_name

        self.update_display()

    def _set_api_key(self, *_):
        api_key: str = self.api_key_input.value
        self.controller.set_api_key(api_key)

    def _retrieve_collection(self, *_):
        collection_id: str = self.collection_id_input.value
        self.view_handler.build_corpus(collection_id, "api")
        self.view_handler.update_displays()
