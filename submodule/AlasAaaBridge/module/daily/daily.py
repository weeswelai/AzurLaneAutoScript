
from module.base.button import ButtonGrid

from submodule.AlasAaaBridge.module.daily.assets import *
from submodule.AlasAaaBridge.module.ui.page import page_daily
from submodule.AlasAaaBridge.module.ui.ui import UI
from module.ocr.ocr import Digit, DigitCounter


DAILY_ENTER_BUTTON_GRID = ButtonGrid(origin=(147, 433), delta=(260, 0), button_shape=(214, 110), grid_shape=(4, 1))
OCR_DAILY_GRID = ButtonGrid(origin=(223, 545), delta=(260, 0), button_shape=(63, 31), grid_shape=(4, 1))
OCR_DAILY = DigitCounter(OCR_DAILY_GRID.buttons, letter=(172, 172, 172), threshold=256, name='DAILY_OCR_GRID', alphabet='01/')
OCR_DAILY_ALLOY = Digit(OCR_ALLOY, name='OCR_ALLOY', letter=(247, 247, 247), threshold=128)



class TrainingDaily(UI):
    def daily_run_once(self):
        self.ui_ensure(page_daily)

    def training_run(self):
        while 1:
            self.daily_run_once()

    def run(self):
        self.training_run()
        self.config.task_delay(server_update=True)
