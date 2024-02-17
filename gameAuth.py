import time, pickle
from selenium.webdriver import ActionChains, Chrome
from selenium.webdriver.common.by import By
from gameStates import BootType
from gameUtils import DataManager


class BootBot:
    def __init__(self, driver: Chrome, data: DataManager, boot_type: BootType):
        self.driver = driver

        if boot_type == BootType.Real:
            self.driver.get("https://casino.bet9ja.com/casino/category/popular")
            Authentication(driver, data).login()
        else:
            self.driver.get(
                "https://logigames.bet9ja.com/Games/Launcher?gameId=11000&provider=0&pff=1&skin=201"
            )


class Authentication:
    def __init__(self, driver, data: DataManager):
        self.driver = driver
        self.data = data
        self.vars = {}

    def wait_for_window(self, timeout=2):
        time.sleep(round(timeout / 1000))
        wh_now = self.driver.window_handles
        wh_then = self.vars["window_handles"]

        if len(wh_now) > len(wh_then):
            return set(wh_now).difference(set(wh_then)).pop()

    def fill_in_login_form(self):
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary-m").click()
        self.driver.find_element(By.ID, "01").click()
        self.driver.find_element(By.ID, "01").send_keys(self.data.get_value("username"))
        self.driver.find_element(By.ID, "02").send_keys(self.data.get_value("password"))
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary-l").click()

    def click_on_live_games(self):
        game = self.driver.find_element(
            By.CSS_SELECTOR, "#\\31 1000 .game__info > .btn-primary-xxs"
        )
        action = ActionChains(self.driver)
        action.move_to_element(game)
        action.perform()
        game.click()

    def switch_to_live_games(self):
        self.vars["win8756"] = self.wait_for_window(2000)
        self.driver.close()
        self.driver.switch_to.window(self.vars["win8756"])
        self.driver.maximize_window()
        self.driver.find_element(By.LINK_TEXT, "Rainbow").click()
        self.driver.find_element(
            By.CSS_SELECTOR, ".col-2:nth-child(3) > .red > .rainbow__ball-value"
        ).click()

    def get_cookies(self):
        # Load cookies from a file
        try:
            with open("cookies.pkl", "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    def save_cookies(self):
        all_cookies = self.driver.get_cookies()

        # Save cookies to a file
        with open("cookies.pkl", "wb") as file:
            pickle.dump(all_cookies, file)

    def add_cookies(self, cookies):
        # Add the loaded cookies to the browser session
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        # reload to reflect cookies
        self.driver.refresh()

    def _login(self):
        cookies = self.get_cookies()

        if not cookies or self.is_cookie_expired(cookies):
            self.login_to_site()
        else:
            self.login_with_cookie(cookies)

    def login(self):
        self.login_to_site()

    def login_to_site(self):
        self.fill_in_login_form()
        self.vars["window_handles"] = self.driver.window_handles

        self.click_on_live_games()
        self.switch_to_live_games()
        self.save_cookies()

        time.sleep(200)

    def is_cookie_expired(self, cookies):
        for cookie in cookies:
            expiration_time = cookie.get("expiry")
            if expiration_time != None:
                if time.time() > expiration_time:
                    return True
        return False

    def login_with_cookie(self, cookies):
        self.driver.get(
            "https://logigames.bet9ja.com/Games/Launcher?gameId=11000&provider=0&pff=0&skin=201"
        )
        self.add_cookies(cookies)
        time.sleep(30)
