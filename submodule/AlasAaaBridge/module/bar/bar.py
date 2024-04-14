from datetime import datetime, timedelta

import cv2
import numpy as np

from module.base.button import ButtonGrid
from module.base.timer import Timer
from module.logger import logger
from module.ocr.ocr import Digit, DigitCounter, Ocr
from submodule.AlasAaaBridge.module.bar.assets import *
from submodule.AlasAaaBridge.module.ui.assets import BACK_ARROW
from submodule.AlasAaaBridge.module.ui.page import page_bar
from submodule.AlasAaaBridge.module.ui.ui import UI


class BarGiftsDigitOcr(Ocr):
    def after_process(self, result):
        result: str = super().after_process(result)
        if result.isdigit():
            return result
        if "X" in result:
            return result[result.index("X") + 1:]


class AffinityDigit(DigitCounter):
    def pre_process(self, image):
        image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        image = cv2.threshold(image, 58, 255, cv2.THRESH_BINARY)[1]
        count, cc = cv2.connectedComponents(image)
        num_idx = [count for count in range(1, count + 1) if
                   50 < np.count_nonzero(cc == count) and count != cc[-1, 0]]
        image = ~(np.isin(cc, num_idx) * 255)  # Numbers are white, need invert
        return image.astype(np.uint8)


GIFTS_GRID = ButtonGrid(origin=(98, 578), delta=(116, 0), button_shape=(93, 93), grid_shape=(9, 1), name='GIFTS')
# GIFTS_OCR_GRID = ButtonGrid(origin=(128, 646), delta=(116, 0), button_shape=(67, 23), grid_shape=(9, 1), name='GIFTS_AMOUNT')
OCR_GIFTS = BarGiftsDigitOcr(GIFTS_GRID.crop((30, 68, 93, 93)).buttons, letter=(247, 247, 247), threshold=128, alphabet="0123456789X", name="GIFTS_AMOUNT")
OCR_AFFINITY = AffinityDigit(OCR_BAR_AFFINITY)
OCR_AFFINITY_LEVEL = Digit(OCR_BAR_AFFINITY_LEVEL, letter=(220, 230, 220), threshold=128, alphabet="0123456789")
OCR_NAME = Ocr(OCR_BAR_ARMS_NAME, lang="cnocr", letter=(255, 54, 0), threshold=128)

WEEKLY_GIFTS = 20
GIFTS_FIRST_BUTTON = GIFTS_GRID.buttons[0]


class Bar(UI):
    _give_count = 0
    _gifts_given = 0
    _last_arms = None
    _last_gifts = 0

    def _appear_BAR_CHECK(self, interval=None):
        # Maybe only one of them will show up
        return self.appear(BAR_CHECK, offset=(20, 20), interval=interval) or \
            self.appear(BAR_CHECK_2, offset=(20, 20), interval=interval)

    def _appear_then_click_BAR_CHECK(self, interval=3):
        return self.appear_then_click(BAR_CHECK, offset=(20 ,20), interval=interval) or \
            self.appear_then_click(BAR_CHECK_2, offset=(20 ,20), interval=interval)

    def _appear_BAR_GIFTS_DETAILS(self, interval=None):
        return self.appear(BAR_GIFTS_GIVE_CHECK, offset=(20, 20), interval=interval) or \
            self.appear(BAR_GIFTS_GIVE, offset=(20, 20), interval=interval)

    def ensure_bar(self, skip_first_screenshot=True):
        """
        Ui check in upper left corner of the bar menu and bar is the same.
        Page:
            in: Any page
            out: BAR_CHECK
        """
        self.ui_ensure(page_bar)
        waie_ui = Timer(1).start()
        self.interval_clear((BACK_ARROW, BAR_MENU, BAR_FILTER_CLICK_SAFE_AREA))
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self._appear_BAR_CHECK():
                break

            if self.appear_then_click(BAR_MENU, offset=(20, 20), interval=3):
                continue

            if self.appear(BAR_ARMS_FILTER, offset=(20, 20), interval=3):
                self.device.click(BAR_FILTER_CLICK_SAFE_AREA)
                continue

            if self.appear(BAR_GIFTS_GRID_CHECK, offset=(20, 20), interval=3) or \
               self._appear_BAR_GIFTS_DETAILS(interval=3) and waie_ui.reached_and_reset():
                self.device.click(BACK_ARROW)
                continue

    def _get_count(self):
        today = datetime.now().weekday() + 1
        if today == 1 and (datetime.now() - timedelta(hours=4, seconds=57)).weekday() + 1 == 7:
            today = 7
        if today == 7 and self.config.AaaBarGiveGifts_WeeklyTaskFinish and \
           WEEKLY_GIFTS - self.config.AaaBarGiveGifts_GiftsGiven >= self.config.AaaBarGiveGifts_GiveCount:
            give_count = WEEKLY_GIFTS - self.config.AaaBarGiveGifts_GiftsGiven
            logger.info(f"Today is Sunday")
        else:
            give_count = self.config.AaaBarGiveGifts_GiveCount
        logger.attr("give count", give_count)
        return give_count

    def get_gifts(self, ocr_result):
        return sum([int(amount) if amount else 0 for amount in ocr_result])

    def check_gifts_amount(self, count):
        """
        Decide how much to give based on amount of gifts,
        if need to finish weekly mission,give more than self.config.AaaBarGiveGifts_GiveCount but not enough gifts,
        check gift that has been given is more than self.config.AaaBarGiveGifts_GiveCount,
        if it is exceeded, end give task, if enable and can finish weekly mission, will finish weekly mission,
        Page:
            out: BAR_GIFTS_GIVE or BAR_GIFTS_GIVE_CHECK
        Return:
            count(int): Gifts that need to be given,
                        False is cannot finish daily or weekly mission
            (bool): Whether to return to bar page redisplay gift list
        """
        logger.attr("gifts need", count)
        result = OCR_GIFTS.ocr(self.device.image)
        self._last_gifts = gifts = self.get_gifts(result)
        daily_need = self.config.AaaBarGiveGifts_GiveCount - self._gifts_given

        # If this time has not gave and gifts is less than daily need
        if gifts < daily_need:
            # On Sunday, gave 18, there are 2 gifts, can finish weekly mission
            if self.config.AaaBarGiveGifts_WeeklyTaskFinish and \
               gifts >= WEEKLY_GIFTS - self.config.AaaBarGiveGifts_GiftsGiven > 0:
                logger.info("No enough gifts to finish daily, but able to finish weekly misson")
                return WEEKLY_GIFTS - self.config.AaaBarGiveGifts_GiftsGiven
            if daily_need >= 0:
                logger.warning("No enough gifts to finish daily or weekly task")
            self._give_count = 0
            return 0
        # On Sunday judging could finish weekly mission, count may exceed 3,
        # Up to 9 gifts can be displayed, and number may be 1, here do not drag gift list for ocr,
        # So we don't know the total number of gifts,
        # gifts need to be given until amount on far right reaches 0.
        if gifts < count and not result[-1] and self.config.AaaBarGiveGifts_WeeklyTaskFinish:
            logger.warning("No enough gifts to finish weekly mission")
            if self._gifts_given < self.config.AaaBarGiveGifts_GiveCount <= gifts:
                logger.info("Finish daily mission")
                return daily_need
            self._give_count = 0
            return 0
        elif gifts < count and result[-1] and self.config.AaaBarGiveGifts_WeeklyTaskFinish:
            logger.info("Unknown total number gifts, give first one first")
            return int(result.pop())
        # gifts >= count
        return count

    def set_dif(self, difference, gifts):
        self._gifts_given += difference  # check_gifts_amount()
        self.config.AaaBarGiveGifts_GiftsGiven += difference  # write config
        self._give_count -= difference
        self._last_gifts = gifts

    def _gifts_give_once(self, count, skip_first_screenshot=True):
        logger.hr("give once")
        skip_ocr = False
        gift_idx = difference = 0
        button = GIFTS_GRID.buttons[gift_idx]
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if not skip_ocr:
                result = OCR_GIFTS.ocr(self.device.image)
                if not result[gift_idx]:
                    gift_idx += 1
                    if gift_idx > 8:  # 8 is ninth gift
                        logger.info("9 gifts use up")
                        return 0
                    button = GIFTS_GRID.buttons[gift_idx]
                gifts = self.get_gifts(result)
                difference = self._last_gifts - gifts

            if difference > 0:
                self.set_dif(difference, gifts)
                count -= difference  # end task
                difference = 0

            if not self._appear_BAR_GIFTS_DETAILS(interval=3) and count:
                self.device.click(button)
                skip_ocr = True
                continue

            if count:
                amount = int(result[gift_idx])
                self.device.multi_click(BAR_GIFTS_GIVE, min(amount, count), interval=(0.3, 0.5))
                skip_ocr = False
            # elif click == 1:
            #     self.device.click(BAR_GIFTS_GIVE)
            #     skip_ocr = False
            else:
                return 0

    def _bar_give_gift(self, count, skip_first_screenshot=True):
        """
        Page:
            in: BAR_GIFTS_GRID_CHECK
            out: BAR_GIFTS_GIVE
        """
        if count <= 0:
            return False
        logger.attr("give count", count)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # Back to bar gift page, redisplay gift list
            if self._appear_BAR_CHECK():
                break

            if not self._appear_BAR_GIFTS_DETAILS(interval=3):
                self.device.click(GIFTS_FIRST_BUTTON)
                continue

            # switch arms
            if self._appear_BAR_GIFTS_DETAILS():
                if not self._gifts_give_once(count):
                    self.ensure_bar()
                    break

    def bar_give_gift(self, skip_first_screenshot=True):
        """
        Page:
            in: Any page
            out: BAR_CHECK or BAR_CHECK_2
        """
        logger.hr("give gift", level=1)
        self.ensure_bar()
        self._give_count = self._get_count()
        self.interval_clear((BAR_CHECK, BAR_CHECK_2, GIFTS_FIRST_BUTTON))
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # Show gifts, usually runs only once
            if self._appear_then_click_BAR_CHECK():
                continue

            if self._appear_BAR_GIFTS_DETAILS():
                count = self.check_gifts_amount(self._give_count)
                self._last_arms = OCR_NAME.ocr(self.device.image)
                logger.attr("arms", self._last_arms)
                self._bar_give_gift(count)  # will back to BAR_CHECK

            if self._give_count <= 0:
                logger.info(f"Task AaaBarGiveGifts is completed")
                break

            if self.appear(BAR_GIFTS_GRID_CHECK, offset=(20, 20), interval=3) \
               and not self._appear_BAR_GIFTS_DETAILS(interval=3):
                self.device.click(GIFTS_FIRST_BUTTON)

    def bar_arms_touch(self):
        self.ensure_bar()

    def run(self):
        if self.config.AaaBarGiveGifts_GiftsGiven < 0:
            logger.warning(f"config.AaaBarGiveGifts_GiftsGiven: {self.config.AaaBarGiveGifts_GiftsGiven}")
            self.config.AaaBarGiveGifts_GiftsGiven = 0
        if self.config.AaaBarGiveGifts_Enable:
            self.bar_give_gift()
            logger.info(f"{self._gifts_given} gifts have been given this time,"
                        f" {self.config.AaaBarGiveGifts_GiftsGiven} gifts have been given this week")
        if self.config.AaaBarTouch_Enable:
            self.bar_arms_touch()
        self.config.task_delay(server_update=True)
