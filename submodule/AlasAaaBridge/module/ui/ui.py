
from module.ui.ui import UI

from submodule.AlasAaaBridge.module.ui.page import *
from submodule.AlasAaaBridge.module.ui.assets import *



class UI(UI):
    def ui_goto_main(self):
        return self.ui_ensure(destination=page_main)