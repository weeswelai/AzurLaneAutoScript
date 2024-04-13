from module.base.timer import Timer
from module.logger import logger
from module.ocr.ocr import Digit
from module.ui.switch import Switch
from submodule.AlasAaaBridge.module.base.base import ModuleBase
from submodule.AlasAaaBridge.module.combat.assets import *
from submodule.AlasAaaBridge.module.exception import AutoCombatIsLocked
from submodule.AlasAaaBridge.module.ui.assets import INFO_POPUP_COMFIRM

COMBAT_PREPARE_CHECK = COMBAT_SUPPLY

OCR_ROUNDS = Digit(OCR_BATTLE_ROUNDS, letter=(228, 228, 228), threshold=128, name='OCR_BATTLE_ROUNDS', alphabet='0123456789')

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
        # Click COMBAT_PREPARE goto ACTING_BATTLE_CHECK is slowly
        acting_check = Timer(1).start()
        self.interval_clear(ACTING_COMBAT, COMBAT_PREPARE)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.appear(ACTING_BATTLE_CHECK):
                break

            if acting_check.reached() and ACTING_PREPARE_SWITCH.appear(self):
                acting_check.reset()
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
        self.set_acting_combat(skip_first_screenshot=skip_first_screenshot)
        skip_first_screenshot = True

        self.interval_clear((BATTLE_STATUS_S, BATTLE_STATUS_A,
                             BATTLE_STATUS_B, INFO_POPUP_COMFIRM))

        show_round = Timer(30).start()
        self.device.screenshot_interval_set('combat')
        OCR_ROUNDS.ocr(self.device.image)

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # TODO Processing timeout, alas's battle timeout is 3 minutes

            if self.appear(BATTLE_AUTO, offset=(20, 20), interval=5):
                raise  # TODO 当前不在代理作战中

            if show_round.reached_and_reset():
                OCR_ROUNDS.ocr(self.device.image)

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
                self.device.screenshot_interval_set()
                break
