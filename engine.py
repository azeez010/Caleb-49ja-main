import os, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from gameAuth import BootBot
from gameUtils import GameLogic, DataManager
from gameSelector import GameSelector, Settings
from gameStates import BootType

from strategy import Strategy

from gameLogger import logger


chrome_options = Options()

chrome_options.add_argument("--headless")
basedir = os.path.abspath(os.path.dirname(__file__))

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])


class Engine:
    def __init__(self):
        logger.info("49ja Program loaded and started")

        Settings()

        self.driver = webdriver.Chrome(options)

        self.loopActive = False

        GameSelector(self)

    def run_strategies(self, draws):
        for strategy in self.strategies:
            strategy.run(draws)

    def check_strategies_wins(self):
        draws = self.logics.result_from_stats_page()
        # draws = self.ballUtils.get_draw_colors()

        for strategy in self.strategies:
            strategy.check_win_and_update_state(draws)

    def start_real(self):
        self.data = DataManager("conf.json")
        self.logics = GameLogic(self.driver, self.data)
        self.strategies: list = Strategy.get_strategies(self.driver, self.data)
        BootBot(self.driver, self.data, BootType.Real)
        self.bot_loop()

    def start_demo(self):
        self.data = DataManager("conf.json")
        self.logics = GameLogic(self.driver, self.data)
        self.strategies: list = Strategy.get_strategies(self.driver, self.data)
        BootBot(self.driver, self.data, BootType.Demo)
        self.bot_loop()

    def close_bot(self):
        time.sleep(3)
        sys.exit(0)

    def track_profit_and_loss(self):
        if not self.loopActive:
            self.logics.set_starting_cash()
        self.loopActive = True

    def bot_loop(self):
        try:
            self.logics.check_time_before_freezing()
            self.track_profit_and_loss()

            while True:
                draws = self.logics.result_from_stats_page()
                self.run_strategies(draws)
                self.logics.freeze_time_for_loop()
                self.check_strategies_wins()
                self.logics.check_finance()
        except Exception as exc:
            self.handle_loop_exception(exc)

    def handle_loop_exception(self, exc):
        logger.critical(
            "some bad happened restarting bot to continue playing", str(exc)
        )
        self.driver.refresh()
        self.bot_loop()
