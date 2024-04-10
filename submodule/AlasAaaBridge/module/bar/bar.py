from datetime import datetime

from module.logger import logger
from module.ocr.ocr import Digit
from submodule.AlasAaaBridge.module.bar.assets import *
from submodule.AlasAaaBridge.module.ui.assets import BACK_ARROW
from submodule.AlasAaaBridge.module.ui.page import page_bar
from submodule.AlasAaaBridge.module.ui.ui import UI

OCR_GIFTS = Digit(OCR_BAR_FIRST_GITF, letter=(247, 247, 247), threshold=128, alphabet="0123456789")


class Bar(UI):
    def _appear_bar_gift_check(self):
        return self.appear(BAR_GIFT_CHECK, offset=(20, 20)) or \
                self.appear(BAR_GIFT_CHECK_2, offset=(20, 20))

    def _appear_then_click_bar_gift_check(self):
        return self.appear_then_click(BAR_GIFT_CHECK, offset=(20 ,20), interval=3) or \
                self.appear_then_click(BAR_GIFT_CHECK_2, offset=(20 ,20), interval=3)

    def ensure_bar_gift(self, skip_first_screenshot=True):
        """
        Ui check in upper left corner of the bar menu and bar is the same.
        Page:
            in: Any page
            out: BAR_GIFT_CHECK
        """
        self.ui_ensure(page_bar)
        self.interval_clear((BACK_ARROW, BAR_MENU, BAR_FILTER_CLICK_SAFE_AREA))
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self._appear_bar_gift_check():
                break

            if self.appear_then_click(BAR_MENU, offset=(20, 20), interval=3):
                continue

            if self.appear(BAR_ARMS_FILTER, offset=(20, 20), interval=3):
                self.device.click(BAR_FILTER_CLICK_SAFE_AREA)
                continue

            if self.appear(BAR_GIFTS_GIVE, offset=(20, 20), interval=3) or\
                self.appear(GIFT_SELECT_CHECK, offset=(20, 20), interval=3):
                self.device.click(BACK_ARROW)
                continue

    def _bar_give_gift(self, count, skip_first_screenshot=True):
        gifts_last = 0
        skip_ocr = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # Back to bar gift page
            if self.appear(BAR_GIFT_CHECK, offset=(20, 20)) or \
                self.appear(BAR_GIFT_CHECK_2, offset=(20, 20)):
                break

            if not skip_ocr:
                gifts = OCR_GIFTS.ocr(self.device.image)

            gifts_given = gifts_last - gifts
            if gifts_given > 0:
                count -= gifts_given
                self.config.AaaBarGiveGifts_GiftsGiven += gifts_given

            if gifts <= 0 or count <= 0 and self.appear(GIFT_SELECT_CHECK, offset=(20, 20), interval=3):
                self.device.click(BACK_ARROW)
                skip_ocr = True
                continue

            gifts_last = gifts
            self.device.multi_click(BAR_GIFTS_GIVE, min(gifts, count), interval=(0.3, 0.5))
        return count

    def bar_give_gift(self, skip_first_screenshot=True):
        self.ensure_bar_gift()
        today = datetime.now().weekday() + 1
        if today == 7 and self.config.AaaBarGiveGifts_WeeklyTaskFinish and \
            20 - self.config.AaaBarGiveGifts_GiftsGiven >= 0:
            give_count = 20 - self.config.AaaBarGiveGifts_GiftsGiven
        else:
            give_count = self.config.AaaBarGiveGifts_GiveCount
        self.interval_clear((BAR_GIFT_CHECK, BAR_GIFT_CHECK_2, BAR_FIRST_GITF, BAR_GIFTS_GIVE))
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self._appear_then_click_bar_gift_check():
                continue

            if self.appear(GIFT_SELECT_CHECK, offset=(20, 20), interval=3):
                self.device.click(BAR_FIRST_GITF)

            if self.appear(BAR_GIFTS_GIVE, offset=(20, 20), interval=3):
                logger.attr("gifts give", give_count)
                give_count = self._bar_give_gift(give_count)

            if not give_count:
                break

    def arms_touch(self):
        self.ensure_bar_gift()

    def run(self):
        if self.config.AaaBarGiveGifts_Enable:
            self.bar_give_gift()
        if self.config.AaaBarTouch_Enable:
            self.arms_touch()
        self.config.task_delay(server_update=True)
