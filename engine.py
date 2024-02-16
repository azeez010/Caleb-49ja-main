import os, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from gameAuth import BootBot
from gameUtils import GameLogic, DataManager
from gameSelector import GameSelector, Settings
from gameStates import BootType

from strategy import Strategy


chrome_options = Options()

chrome_options.add_argument("--headless")
basedir = os.path.abspath(os.path.dirname(__file__))

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])


class Engine:
    def __init__(self):

        Settings()

        self.driver = webdriver.Chrome(options)

        self.loopActive = False

        GameSelector(self)

    def run_strategies(self):
        for strategy in self.strategies:
            strategy.run()

    def check_strategies_wins(self):
        for strategy in self.strategies:
            strategy.check_win_and_update_state()

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
                self.run_strategies()
                self.logics.freeze_time_for_loop()
                self.check_strategies_wins()
                self.logics.check_finance()
        except Exception as exc:
            self.handle_loop_exception(exc)

    def handle_loop_exception(self, exc):
        print("some bad happened restarting bot to continue playing", str(exc))
        self.driver.refresh()
        self.bot_loop()
