from module.base.timer import Timer
from module.logger import logger
from submodule.AlasAaaBridge.module.combat.assets import GET_ITEM
from submodule.AlasAaaBridge.module.reward.assets import *
from submodule.AlasAaaBridge.module.ui.assets import CITY_BAR_ENTRANCE
from submodule.AlasAaaBridge.module.ui.page import (page_city, page_main,
                                                    page_reward)
from submodule.AlasAaaBridge.module.ui.ui import UI


class Reward(UI):
    def select_mission_all(self, skip_first_screenshot=False):
        self.interval_clear(MISSION_ALL_NOT_SELECT)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(MISSION_ALL_NOT_SELECT, offset=(20, 20), interval=5):
                self.device.click(MISSION_ALL_SELECT)
                continue

            if self.appear(MISSION_ALL_SELECT, offset=(20, 20)):
                break

    def reward_mission_run(self, skip_first_screenshot=False):
        logger.hr('Mission receive')
        self.ui_ensure(page_reward)
        self.select_mission_all(skip_first_screenshot=True)
        skip_first_screenshot = True
        confirm_timer = Timer(1.5, count=3).start()
        self.interval_clear((MISSION_ALL_FINISH, GET_ITEM))

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear_then_click(MISSION_ALL_FINISH, offset=(20, 20), interval=5):
                continue

            if self.appear(GET_ITEM, offset=(20, 20), interval=3):
                self.device.click(MISSION_CLICK_SAFE_AREA)
                confirm_timer.reset()
                continue

            if confirm_timer.reached() and self.appear(MISSION_ALL_RECEIVED, offset=(20, 20)):
                break

        logger.info('Reward mission receive end')

    def reward_city_run(self, skip_first_screenshot=False):
        logger.hr('Reward city receive')
        # Must first go to main page before entering city page
        self.ui_ensure(page_main)
        self.ui_ensure(page_city)
        ui_wait = Timer(3, count=3).start()  # Wait all ui loading completed
        confirm_timer = Timer(3, count=3).start()
        # Set click interval to 0.3, because game can't respond that fast.
        click_timer = Timer(0.3)
        self.interval_clear((CITY_REVENUE, CITY_PARTS, CITY_REVENUE))

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if not ui_wait.reached():
                confirm_timer.reset()

            if click_timer.reached() and self.appear_then_click(CITY_REVENUE, offset=(20, 20), interval=60):
                confirm_timer.reset()
                click_timer.reset()
                continue
            if click_timer.reached() and self.appear_then_click(CITY_PARTS, offset=(20, 20), interval=60):
                confirm_timer.reset()
                click_timer.reset()
                continue
            if click_timer.reached() and self.appear_then_click(CITY_ALLOY, offset=(20, 20), interval=60):
                confirm_timer.reset()
                click_timer.reset()
                continue

            # End
            if self.appear(CITY_BAR_ENTRANCE, offset=(20, 20)) and confirm_timer.reached():
                break

        logger.info('Reward city receive end')

    def run(self):
        self.reward_mission_run()
        self.reward_city_run()
        self.config.task_delay(success=True)
