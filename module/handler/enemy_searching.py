from module.base.timer import Timer
from module.base.utils import red_overlay_transparency, get_color
from module.handler.assets import *
from module.handler.info_bar import InfoBarHandler
from module.logger import logger
from module.exception import CampaignEnd
from module.ui.assets import CAMPAIGN_GOTO_DAILY


class EnemySearchingHandler(InfoBarHandler):
    MAP_ENEMY_SEARCHING_OVERLAY_TRANSPARENCY_THRESHOLD = 0.5  # Usually (0.70, 0.80).
    MAP_ENEMY_SEARCHING_TIMEOUT_SECOND = 4.5
    in_stage_timer = Timer(1)

    def enemy_searching_color_initial(self):
        MAP_ENEMY_SEARCHING.load_color(self.device.image)

    def enemy_searching_appear(self):
        return red_overlay_transparency(
            MAP_ENEMY_SEARCHING.color, get_color(self.device.image, MAP_ENEMY_SEARCHING.area)
        ) > self.MAP_ENEMY_SEARCHING_OVERLAY_TRANSPARENCY_THRESHOLD

    def handle_enemy_flashing(self):
        self.device.sleep(1.2)

    def handle_in_stage(self):
        if self.is_in_stage():
            if self.in_stage_timer.reached():
                logger.info('In stage.')
                self.ensure_no_info_bar(timeout=1.2)
                raise CampaignEnd('In stage.')
        else:
            self.in_stage_timer.reset()
            return False

    def is_in_stage(self):
        return self.appear(IN_STAGE_RED) or self.appear(IN_STAGE_BLUE) or self.appear(CAMPAIGN_GOTO_DAILY)

    def is_in_map(self):
        return self.appear(IN_MAP)

    def handle_in_map_with_enemy_searching(self):
        if not self.is_in_map():
            return False
        if self.handle_in_stage():
            return True

        timeout = Timer(self.MAP_ENEMY_SEARCHING_TIMEOUT_SECOND)
        appeared = False
        while 1:
            timeout.start()
            if self.handle_in_stage():
                return True
            if self.enemy_searching_appear():
                appeared = True
            else:
                if appeared:
                    self.handle_enemy_flashing()
                    self.device.sleep(0.3)
                    logger.info('In map.')
                    break
                self.enemy_searching_color_initial()

            if timeout.reached():
                # logger.warning('Enemy searching timeout.')
                logger.info('Enemy searching timeout.')
                break

            self.device.screenshot()
        return True

    def handle_in_map_no_enemy_searching(self):
        if not self.is_in_map():
            return False
        if self.handle_in_stage():
            return True

        self.device.sleep((1, 1.2))
        return True
