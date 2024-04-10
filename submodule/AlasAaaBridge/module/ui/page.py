from module.ui.page import Page
from submodule.AlasAaaBridge.module.ui.assets import *

MAIN_CHECK = CITY_ENTRANCE
CAMPAIGN_MENU_CHECK = CAMPAIGN_MENU_GOTO_DAILY = TRAINING_DAILY

# Main
page_main = Page(MAIN_CHECK)
page_campaign_menu = Page(CAMPAIGN_MENU_CHECK)
page_main.link(MAIN_GOTO_CAMPAIGN, destination=page_campaign_menu)
page_campaign_menu.link(button=GOTO_MAIN, destination=page_main)

# Unknown
page_unknown = Page(None)
page_unknown.link(button=GOTO_MAIN, destination=page_main)

# Daily
# TODO test: # Don't enter page_daily_menu from page_campaign
page_daily_menu = Page(DAILY_MENU_CHECK)
page_daily_menu.link(button=GOTO_MAIN, destination=page_main)
page_daily_menu.link(button=BACK_ARROW, destination=page_campaign_menu)
page_campaign_menu.link(button=CAMPAIGN_MENU_GOTO_DAILY, destination=page_daily_menu)
page_daily = Page(DAILY_CHECK)
page_daily.link(button=GOTO_MAIN, destination=page_main)
page_daily.link(button=BACK_ARROW, destination=page_daily_menu)

# Reward
page_reward = Page(MISSION_CHECK)
page_reward.link(button=GOTO_MAIN, destination=page_main)
page_main.link(MISSION_ENTER, destination=page_reward)

# City
page_city = Page(CITY_CHECK)
page_city.link(button=GOTO_MAIN, destination=page_main)
page_main.link(CITY_ENTRANCE, destination=page_city)

# Bar
page_bar = Page(BAR_CHECK)
page_bar.link(button=GOTO_MAIN, destination=page_main)
page_bar.link(button=BACK_ARROW, destination=page_city)
page_city.link(button=CITY_BAR_ENTRANCE, destination=page_bar)
