from submodule.AlasAaaBridge.module.combat.assets import GET_ITEM
from submodule.AlasAaaBridge.module.reward.assets import *
from submodule.AlasAaaBridge.module.ui.page import page_reward
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

    def reward_run(self, skip_first_screenshot=False):
        self.ui_ensure(page_reward)
        self.select_mission_all(skip_first_screenshot=True)
        skip_first_screenshot = True
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

            if self.appear(MISSION_ALL_RECEIVED, offset=(20, 20)):
                break

    def run(self):
        self.reward_run()
        self.config.task_delay(minute=60)
