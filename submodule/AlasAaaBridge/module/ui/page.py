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
# TODO test: # Don't enter page_daily from page_campaign
page_daily = Page(DAILY_CHECK)
page_daily.link(button=GOTO_MAIN, destination=page_main)
page_daily.link(button=BACK_ARROW, destination=page_campaign_menu)
page_campaign_menu.link(button=CAMPAIGN_MENU_GOTO_DAILY, destination=page_daily)
page_daily_enter = Page(DAILY_ENTER_CHECK)
page_daily_enter.link(button=GOTO_MAIN, destination=page_main)
page_daily_enter.link(button=BACK_ARROW, destination=page_daily)
