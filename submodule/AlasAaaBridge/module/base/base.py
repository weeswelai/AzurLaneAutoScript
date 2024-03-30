from module.base.base import ModuleBase
from submodule.AlasAaaBridge.module.config.config import AshArmsConfig


class ModuleBase(ModuleBase):
    config: AshArmsConfig
