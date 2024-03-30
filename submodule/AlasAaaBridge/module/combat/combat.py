from module.logger import logger
from module.ui.switch import Switch
from submodule.AlasAaaBridge.module.base.base import ModuleBase
from submodule.AlasAaaBridge.module.combat.assets import *
from submodule.AlasAaaBridge.module.exception import AutoCombatIsLocked
from submodule.AlasAaaBridge.module.ui.assets import INFO_POPUP_COMFIRM

COMBAT_PREPARE_CHECK = COMBAT_SUPPLY


ACTING_PREPARE_SWITCH = Switch("COMBAT_AUTO_PREPARE")
ACTING_PREPARE_SWITCH.add_status("ready", ACTING_COMBAT_READY, ACTING_COMBAT)
ACTING_PREPARE_SWITCH.add_status("not_ready", ACTING_COMBAT)
ACTING_PREPARE_SWITCH.add_status("locked", ACTING_COMBAT_LOCKED)


class Combat(ModuleBase):
    def set_acting_combat(self, skip_first_screenshot=False):
        """
        Page:
            in: COMBAT_PREPARE_CHECK
        """
        self.interval_clear(ACTING_COMBAT, COMBAT_PREPARE)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(ACTING_BATTLE_CHECK):
                break

            if ACTING_PREPARE_SWITCH.appear(self):
                if ACTING_PREPARE_SWITCH.get(self) == "locked":
                    raise AutoCombatIsLocked  # TODO handle AutoCombatIsLocked
                ACTING_PREPARE_SWITCH.set("ready", self, skip_first_screenshot=True)

            if self.appear(COMBAT_PREPARE_LOCKED, offset=(20, 20), interval=3):
                # TODO 处理 职能, 编队补充, 体力不足
                continue

            if self.appear_then_click(COMBAT_PREPARE, offset=(20, 20), interval=3):
                continue

    def handle_battle_status(self):
        if self.appear_then_click(BATTLE_STATUS_S, interval=5):
            return True
        elif self.appear_then_click(BATTLE_STATUS_A, interval=5):
            logger.warning('Battle status: A')
            return True
        elif self.appear_then_click(BATTLE_STATUS_B, interval=5):
            logger.warning('Battle status: B')
            return True

    def acting_combat(self, break_button=None, offset=(20, 20), skip_first_screenshot=False):
        """
        Page:
            in: COMBAT_PREPARE_CHECK
            out: break_button
        """
        round = 0
        self.set_acting_combat(skip_first_screenshot=skip_first_screenshot)
        skip_first_screenshot = True

        self.interval_clear(BATTLE_STATUS_S, BATTLE_STATUS_A,
                            BATTLE_STATUS_B, INFO_POPUP_COMFIRM)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # round = # TODO ocr round

            # TODO Processing timeout, alas's battle timeout is 3 minutes

            if self.appear(ACTING_BATTLE_CHECK, offset=(20, 20), interval=5):
                continue

            if self.handle_battle_status():
                continue

            # TODO handle get new arms popup

            if self.appear(GET_ITEM, offset=(20, 20), interval=5):
                self.device.click(BATTLE_STATUS_S)
                continue

            if self.appear_then_click(INFO_POPUP_COMFIRM, interval=5):
                continue

            if self.appear(break_button, offset=offset):
                break
