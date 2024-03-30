
from module.ui.ui import UI
from submodule.AlasAaaBridge.module.config.config import AshArmsConfig
from submodule.AlasAaaBridge.module.ui.assets import *
from submodule.AlasAaaBridge.module.ui.page import *


class UI(UI):
    config: AshArmsConfig

    def ui_goto_main(self):
        return self.ui_ensure(destination=page_main)
