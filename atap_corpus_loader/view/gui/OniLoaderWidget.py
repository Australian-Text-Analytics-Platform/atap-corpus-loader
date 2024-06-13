from panel import Row, Column
from panel.layout import Divider
from panel.pane import Markdown
from panel.widgets import Select, TextInput, Button, PasswordInput

from atap_corpus_loader.controller import Controller
from atap_corpus_loader.view import ViewWrapperWidget
from atap_corpus_loader.view.gui import AbstractWidget, FileLoaderWidget


class OniLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget, controller: Controller, include_meta_loader: bool):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler
        self.controller: Controller = controller

        provider_tooltip = self.view_handler.get_tooltip('oni_provider')
        self.provider_selector = Select(name='Provider selector', width=150)
        self.provider_selector.param.watch(self._on_provider_change, ['value'])

        self.toggle_add_provider_button = Button(name='Add new provider', width=150, button_type='primary', button_style='outline', align='center')
        self.toggle_add_provider_button.on_click(self._toggle_show_add_provider_pane)

        self.add_provider_name_input = TextInput(name='Provider name', placeholder='Provider name, e.g. MyProvider', visible=False)
        self.add_provider_address_input = TextInput(name='Provider address', placeholder='Provider address, e.g. https://data.ldaca.edu.au', visible=False)
        self.add_provider_button = Button(name='Add', button_type='success', button_style='solid', visible=False)
        self.add_provider_button.on_click(self._add_provider)
        self.add_provider_panel: Column = Column(self.add_provider_name_input,
                                                 self.add_provider_address_input,
                                                 self.add_provider_button,
                                                 visible=False)

        api_key_tooltip = self.view_handler.get_tooltip('oni_api_key')
        self.api_key_input = PasswordInput(name='API Key', placeholder='af6391e0-f873-11ee-8355-bae397411a92')
        self.api_key_input.param.watch(self._set_api_key, ['value'])

        retrieve_collection_tooltip = self.view_handler.get_tooltip('oni_retrieve_collection')
        self.collection_id_input = TextInput(name='Collection ID', placeholder='arcp://name,doi10.26180%2F23961609')
        self.retrieve_collection_button = Button(name='Retrieve collection information', button_type='success', button_style='solid', align='end')
        self.retrieve_collection_button.on_click(self._retrieve_collection_information)

        self.file_loader: FileLoaderWidget = FileLoaderWidget(view_handler, controller, include_meta_loader)

        self.curr_provider_display = Markdown(stylesheets=["a { margin: 0;}"])

        self.panel = Column(
            Row(self.provider_selector,
                self.curr_provider_display,
                self.toggle_add_provider_button,
                provider_tooltip),
            Row(self.add_provider_panel),
            Row(self.api_key_input,
                api_key_tooltip),
            Row(self.collection_id_input,
                self.retrieve_collection_button,
                retrieve_collection_tooltip),
            Divider(),
            Row(self.file_loader),
            sizing_mode='stretch_width'
        )
        self.children = [self.file_loader]
        self.update_display()

    def update_display(self):
        self.provider_selector.options = self.controller.get_providers()
        self.provider_selector.value = self.controller.get_curr_provider()
        curr_provider_address = self.controller.get_curr_provider_address()
        link = f'<a href="{curr_provider_address}" target="_blank">{curr_provider_address}</a>'
        self.curr_provider_display.object = link

    def _on_provider_change(self, *_):
        self.controller.set_curr_provider(self.provider_selector.value)
        curr_provider_address = self.controller.get_curr_provider_address()
        link = f'<a href="{curr_provider_address}" target="_blank">{curr_provider_address}</a>'
        self.curr_provider_display.object = link

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

    def _retrieve_collection_information(self, *_):
        collection_id: str = self.collection_id_input.value
        self.controller.set_collection_id(collection_id)
        self.file_loader.unload_all()
        self.view_handler.update_displays()
