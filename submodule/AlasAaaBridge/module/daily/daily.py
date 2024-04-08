from datetime import datetime

import cv2

from module.base.button import ButtonGrid
from module.logger import logger
from module.ocr.ocr import Digit, DigitCounter
from module.ui.scroll import Scroll
from submodule.AlasAaaBridge.module.combat.combat import COMBAT_PREPARE_CHECK, Combat
from submodule.AlasAaaBridge.module.daily.assets import *
from submodule.AlasAaaBridge.module.ui.assets import (DAILY_CHECK,
                                                      DAILY_ENTER_CHECK)
from submodule.AlasAaaBridge.module.ui.page import page_daily
from submodule.AlasAaaBridge.module.ui.ui import UI

DAILY_ENTER_BUTTON_GRID = ButtonGrid(origin=(147, 433), delta=(260, 0), button_shape=(214, 110), grid_shape=(4, 1))
OCR_DAILY_GRID = ButtonGrid(origin=(223, 545), delta=(260, 0), button_shape=(63, 31), grid_shape=(4, 1))
OCR_DAILY_ALLOY = Digit(OCR_ALLOY, name='OCR_ALLOY', letter=(247, 247, 247), threshold=128)
DAILY_SCROLL = Scroll(DAILY_SCROLL_AREA, color=(96, 96, 96), name='DAILY_SCROLL_AREA')
DAILY_DIFFICULTY_GRID = ButtonGrid(origin=(950, 129), delta=(0, 182), button_shape=(108, 94), grid_shape=(1, 3))


class OcrDaily(DigitCounter):
    def pre_process(self, image):
        image = super().pre_process(image)
        return cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)[1]


def _get_training_attr():
    today = datetime.now().weekday() + 1
    if today in (1, 3, 5):
        hunting = "AaaTrainingDaily_HuntingLand"
    if today in (2, 4, 6):
        hunting = "AaaTrainingDaily_HuntingAir"
    if today == 7:
        hunting = "AaaTrainingDaily_HuntingLandAndAir"
    return {
        0: "AaaTrainingDaily_BattleExercises",
        1: hunting,
        2: "AaaTrainingDaily_ExpansionTraining",
        3: "AaaTrainingDaily_Resourcepreparation"
    }


class TrainingDaily(Combat, UI):
    def enter_daily_detail(self, count, skip_first_screenshot=False):
        """
        Pages:
            in: page_daily
            out: DAILY_ENTER_CHECK
        """
        enter_button = DAILY_ENTER_BUTTON_GRID.buttons[count]
        self.interval_clear(DAILY_CHECK)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if self.appear(DAILY_ENTER_CHECK, offset=(20, 20)):
                break

            if self.appear(DAILY_CHECK, offset=(20, 20), interval=3):
                self.device.click(enter_button)

    def scroll_set_bottom(self, skip_first_screenshot=False):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if DAILY_SCROLL.at_bottom(main=self):
                break

            if DAILY_SCROLL.set_bottom(main=self, skip_first_screenshot=True):
                continue

    def daily_combat_enter(self, difficulty, skip_first_screenshot=False):
        """
        Pages:
            in: DAILY_ENTER_CHECK
            out: combat main
        """
        # When slider is at top or bottom, there are 3 fixed buttons,
        # corresponding to difficulty 1, 2, 3 at top,
        # difficulty 4, 5, 6 at bottom.
        if difficulty >= 4:
            count = difficulty - 4
            self.scroll_set_bottom()
        else:
            count = difficulty - 4

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()
            if self.appear(DAILY_ENTER_CHECK, offset=(20, 20), interval=3):
                self.device.click(DAILY_DIFFICULTY_GRID.buttons[count])

            if self.appear(COMBAT_PREPARE_CHECK, offset=(20, 20)):
                break

    def _get_daily_ocr(self, count):
        return OcrDaily(OCR_DAILY_GRID.buttons[count], letter=(1, 50, 1), threshold=128, name='DAILY_OCR_GRID', alphabet='01/')

    def training_run(self):
        """
        Page:
            out: page_daily
        """
        current = 0
        daily = _get_training_attr()
        while 1:
            self.ui_ensure(page_daily)
            if current > 3:
                break
            difficulty = getattr(self.config, daily[current])
            logger.attr(daily[current], difficulty)
            remain, _, _ = self._get_daily_ocr(current).ocr(self.device.image)
            # difficulty will be 0, 1, 2, 3, 4, 5, 6. 0 mean not combat

            if OCR_DAILY_ALLOY.ocr(self.device.image) < 150:
                logger.info("ALLOY less than 150, delay task")
                # TODO 体力不足150, 延迟任务并调度收获任务
                pass

            if remain > 0:
                if difficulty > 0:
                    logger.hr(daily[current], 3)
                    self.enter_daily_detail(current, skip_first_screenshot=True)
                    self.daily_combat_enter(difficulty)
                    self.acting_combat(break_button=DAILY_ENTER_CHECK,
                                       skip_first_screenshot=True)
                else:
                    logger.info("difficulty set 0, no combat")

            current += 1

    def run(self):
        self.training_run()
        self.config.task_delay(server_update=True)
