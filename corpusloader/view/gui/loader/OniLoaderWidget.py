from panel import Row

from corpusloader.view import ViewWrapperWidget
from corpusloader.view.gui import AbstractWidget
from corpusloader.view.gui.styles import oni_loader_style


class OniLoaderWidget(AbstractWidget):
    def __init__(self, view_handler: ViewWrapperWidget):
        super().__init__()
        self.view_handler: ViewWrapperWidget = view_handler

        self.component = Row(None,
                             styles=oni_loader_style)

    def update_display(self):
        pass
