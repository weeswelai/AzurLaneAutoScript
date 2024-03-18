# Aaa

# 每日
每天做一次就可以的任务

## 训练所
战斗演习  battle exercises
狩猎行动-地面  Hunting - Ground
狩猎行动-空域  Hunting - Air
拓展训练  Expansion training
资源筹备  Resource preparation

## 探索

## 酒馆
bar
送礼以及摸头

## 仓库每日
开资源箱
开加密箱
分解开发套件
合成框架
合成插件

# 收获
时不时上线的任务

## 火车

## 意识工厂

## 维修会
回收arms

# 周常
## 飞艇远征

# 奖励
## 收获资源

## 领取每日任务
每日以及周常奖励领取

## 邮箱领取

## 大月卡



# Alas module

## TODO
这一段的 `detect_package` 在 auto 情况下如何灰烬战线的包? 待测试
`set_server` 与碧蓝耦合
```py
        # Package
        self.package = self.config.Emulator_PackageName
        if self.package == 'auto':
            self.detect_package()
        else:
            set_server(self.package)
```

## Config
要设置 `config.py`里的`AshArmsConfig`类中
`SCHEDULER_PRIORITY` 成员变量, 这个是优先级,不写则任务不会出现在等待任务中

`alas_device_lock` 方法中要给args.json字典添加3个字段, 
```json
"type": "lock",
"value": "lock"
```
否则模拟器adb地址前会被添加一个 `\b`

保存的时候会被添加进json文件里, 要在 `save`函数里删掉
