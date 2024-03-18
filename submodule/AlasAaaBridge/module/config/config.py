import os
from datetime import datetime

from module.config.config import AzurLaneConfig, name_to_function
from module.config.utils import filepath_config, deep_get
from submodule.AlasAaaBridge.module.config.config_generated import GeneratedConfig
from submodule.AlasAaaBridge.module.config.config_updater import ConfigUpdater


class AshArmsConfig(AzurLaneConfig, ConfigUpdater, GeneratedConfig):
    SCHEDULER_PRIORITY = """
        Restart
      > AaaTrainingDaily
      > AaaExploration
      > AaaMainDaily
      > AaaTrain
    """

    def __init__(self, config_name, task=None):
        super().__init__(config_name, task)
        if task is None:
            task = name_to_function("Aaa")
            self.bind(task)
            self.task = task
            self.save()
            self.args

    def bind(self, func, func_list=None):
        if func_list is None:
            func_list = ['Aaa']
        super().bind(func, func_list)

    def save(self, mod_name='aaa'):
        if deep_get(self.data, "Aaa.AlasLock"):
            del(self.data["Aaa"]["AlasLock"])
        super().save(mod_name)

    def get_mtime(self):
        timestamp = os.stat(filepath_config(self.config_name, mod_name='aaa')).st_mtime
        mtime = datetime.fromtimestamp(timestamp).replace(microsecond=0)
        return mtime


def load_config(config_name, task):
    return AshArmsConfig(config_name, task)
