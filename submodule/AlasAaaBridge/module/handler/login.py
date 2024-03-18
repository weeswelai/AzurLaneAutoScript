from module.base.timer import Timer
from module.handler.login import LoginHandler
from module.logger import logger
from submodule.AlasAaaBridge.module.handler.assets import *
from submodule.AlasAaaBridge.module.ui.assets import MAIN_GOTO_CAMPAIGN, GOTO_MAIN

MAIN_CHECK = MAIN_GOTO_CAMPAIGN


class LoginHandler(LoginHandler):
    def _handle_app_login(self):
        """
        Pages:
            in: Any page
            out: page_main
        """
        logger.hr('App login')

        confirm_timer = Timer(1.5, count=4).start()
        orientation_timer = Timer(5)
        login_success = False

        while 1:
            # Watch device rotation
            if not login_success and orientation_timer.reached():
                # Screen may rotate after starting an app
                self.device.get_orientation()
                orientation_timer.reset()

            self.device.screenshot()

            # End
            if self.appear(MAIN_CHECK, offset=(30, 30)):
                if confirm_timer.reached():
                    logger.info('Login to main confirm')
                    break
            else:
                confirm_timer.reset()

            # Login
            if self.appear(LOGIN_CHECK, offset=(30, 30), interval=5) and LOGIN_CHECK.match_appear_on(self.device.image):
                self.device.click(LOGIN_CHECK)
                if not login_success:
                    logger.info('Login success')
                    login_success = True

            # update
            if self.appear_then_click(LOGIN_UPDATE, offset=(30, 30), interval=5):
                continue

            # Announcement
            if self.appear(LOGIN_ANNOUNCE, offset=(30, 30), interval=3):
                # Today
                if self.appear_then_click(LOGIN_ANNOUNCE_BUTTON, offset=(30, 30), interval=3):
                    continue
                self.device.click(LOGIN_SAFE_AREA)
                continue

            # Get rewards for sign in
            if self.appear(ITEM_GET, offset=(30, 30), interval=3) or \
                self.appear(LOGIN_ITEM_MESSAGE_CHECK, offset=(30, 30), interval=3):
                self.device.click(LOGIN_SAFE_AREA)
                continue
            
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30), interval=3):
                continue






    


