import time

from selenium.webdriver import Chrome, ActionChains
from gameUtils import DataManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from gameStates import ButtonLabels


class GameActions:
    def __init__(self, driver: Chrome, data: DataManager):
        self.driver = driver

    def click_on_link_text(self, link_text):
        self.driver.find_element(By.LINK_TEXT, link_text).click()

    def get_bets_count(self):
        self.driver.implicitly_wait(0)
        return len(self.driver.find_elements(By.CLASS_NAME, "bets__item"))

    def place_bet(self):
        initial_count = self.get_bets_count()

        retry_attempts = 3  # Adjust the number of retry attempts as needed

        for _ in range(retry_attempts):
            # Perform the action that may increase the count (e.g., clicking a button)
            self._place_bet()

            # Wait for the new count to be greater than the initial count
            wait = WebDriverWait(self.driver, 6)

            try:
                wait.until(lambda driver: self.get_bets_count() > initial_count)
            except:
                pass

            # Get the new count
            new_count = self.get_bets_count()

            # Check if the count has increased by 1
            if new_count == initial_count + 1:
                # print("Count increased by 1. Proceed.")
                return True
            else:
                # print("Count did not increase by 1. Retrying...")
                time.sleep(2)
        return False

    def _place_bet(self):
        element = self.driver.find_element(By.LINK_TEXT, "Place bet")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()

    def click_3plus_ball(self, color):
        self.driver.find_element(
            By.CSS_SELECTOR, f".col-2:nth-child(3) > .{color} > .rainbow__ball-value"
        ).click()

    def check_if_clickable_is_not_active(self, clickable):
        element_class = clickable.get_attribute("class")
        if "active" in element_class.split():
            return False
        return True

    def click_blue(self):
        self.click_on_link_text(ButtonLabels.TotalColor.value)
        self.check_and_click(
            self.driver.find_element(By.CSS_SELECTOR, ".g-total__btn:nth-child(2)")
        )

    def click_red(self):
        self.click_on_link_text(ButtonLabels.TotalColor.value)
        self.check_and_click(
            self.driver.find_element(By.CSS_SELECTOR, ".g-total__btn:nth-child(3)")
        )

    def click_green(self):
        self.click_on_link_text(ButtonLabels.TotalColor.value)
        self.check_and_click(
            self.driver.find_element(By.CSS_SELECTOR, ".g-total__wrap > .green")
        )

    def click_draw(self):
        self.click_on_link_text(ButtonLabels.TotalColor.value)
        self.check_and_click(
            self.driver.find_element(By.CSS_SELECTOR, ".black:nth-child(1)")
        )

    def check_and_click(self, button):
        if self.check_if_clickable_is_not_active(button):
            button.click()

    def enter_stake(self, stake):
        stake_input = self.driver.find_element(
            By.CSS_SELECTOR,
            ".stakes__body-column:nth-child(1) > .input-group:nth-child(1) > input",
        )
        stake_input.send_keys(Keys.CONTROL + "a")
        stake_input.clear()

        self.driver.find_element(
            By.CSS_SELECTOR,
            ".stakes__body-column:nth-child(1) > .input-group:nth-child(1) > input",
        ).send_keys(stake)
        self.forcefully_clear_stake(stake)

    def forcefully_clear_stake(self, stake):
        stake_input = self.driver.find_element(
            By.CSS_SELECTOR,
            ".stakes__body-column:nth-child(1) > .input-group:nth-child(1) > input",
        )

        if stake_input.get_attribute("value") != str(stake):
            stake_input.send_keys(
                Keys.BACKSPACE * len(stake_input.get_attribute("value"))
            )
            stake_input.send_keys(stake)

    def rainbow_color(self, color, color_num=4):
        self.driver.find_element(
            By.CSS_SELECTOR,
            f".col-2:nth-child({color_num}) > .{color} > .rainbow__ball-value",
        ).click()

    def play3_game(self, color, stake):
        self.click_3plus_ball(color)
        self.enter_stake(stake)
        bet_placed = self.place_bet()
        self.click_3plus_ball(color)
        return bet_placed

    def play_rainbow_game(self, color, stake):
        self.rainbow_color(color)
        self.enter_stake(stake)

        bet_placed = self.place_bet()

        time.sleep(2)
        self.rainbow_color(color)
        return bet_placed

    def play_totalcolor_game(self, color, stake):
        if hasattr(self, f"click_{color}"):
            getattr(self, f"click_{color}")()
            self.enter_stake(stake)
            bet_placed = self.place_bet()
            time.sleep(2)
            return bet_placed

        raise ValueError(f"Color method {color} does not exist")
