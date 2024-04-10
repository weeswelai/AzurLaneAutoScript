from alas import AzurLaneAutoScript
from cached_property import cached_property
from module.exception import RequestHumanTakeover
from module.logger import logger
from submodule.AlasAaaBridge.module.config.config import AshArmsConfig


class AshArmsAgent(AzurLaneAutoScript):
    @cached_property
    def config(self):
        try:
            config = AshArmsConfig(config_name=self.config_name)
            return config
        except RequestHumanTakeover:
            logger.critical("Request human takeover")
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    @cached_property
    def device(self):
        try:
            from module.device.device import Device
            device = Device(config=self.config)
            device.stuck_long_wait_list = ['BATTLE_STATUS_S', 'ACTING_BATTLE_CHECK', 'BATTLE_AUTO', 'LOGIN_CHECK']
            return device
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    def restart(self):
        from submodule.AlasAaaBridge.module.handler.login import LoginHandler
        LoginHandler(config=self.config, device=self.device).app_restart()

    def aaa_training_daily(self):
        from submodule.AlasAaaBridge.module.daily.daily import TrainingDaily
        TrainingDaily(config=self.config, device=self.device).run()

    def aaa_reward(self):
        from submodule.AlasAaaBridge.module.reward.reward import Reward
        Reward(config=self.config, device=self.device).run()

    def goto_main(self):
        from submodule.AlasAaaBridge.module.handler.login import LoginHandler
        from submodule.AlasAaaBridge.module.ui.ui import UI
        if self.device.app_is_running():
            logger.info('App is already running, goto main page')
            UI(self.config, device=self.device).ui_goto_main()
        else:
            logger.info('App is not running, start app and goto main page')
            LoginHandler(self.config, device=self.device).app_start()
            UI(self.config, device=self.device).ui_goto_main()


def loop(config_name):
    AshArmsAgent(config_name).loop()


def set_stop_event(e):
    AshArmsAgent.stop_event = e
