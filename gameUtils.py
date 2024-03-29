import time, json, sys, os
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from gameStates import GameStateType, DataConfigState
from gameNotification import Notification, MessageTemplate
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from gameLogger import logger


class GameUtils:
    def __init__(self, driver: Chrome, data):
        self.driver = driver
        self.data = data
        self.wait = WebDriverWait(self.driver, 5)

        self.last_draw = []

    @property
    def get_account_balance(self):
        self.driver.implicitly_wait(10)
        cash = self.driver.find_element(
            By.XPATH, "//div[@class='rs-menu__balance-value']"
        )
        return int(float(cash.find_element(By.TAG_NAME, "span").text))

    @property
    def get_time(self):
        time = self.driver.find_element(
            By.XPATH, "//div[@class='timeline__value-txt']"
        ).text
        return int(time) if time else 0


class GameLogic(GameUtils):
    def check_time(self, min_time, max_time):
        game_time = self.get_time
        if game_time > min_time and game_time < max_time:
            return True
        return False

    def set_starting_cash(self):
        self.data.update_value(
            DataConfigState.StartCash.value, self.get_account_balance
        )

    def check_time_before_freezing(self, additional_time=15):
        time.sleep(self.get_time + additional_time)

    def freeze_time_for_loop(self, additional_time=15):
        time.sleep(self.get_time + additional_time)

    def freeze_time(self, freeze_time=5):
        time.sleep(freeze_time)

    def check_balance(self, num_of_games: int, bet_price: int, strategy_name: str = ""):
        bet_price *= num_of_games
        balance = self.get_account_balance
        if bet_price > balance:
            # Generate message template for take profit
            get_template = MessageTemplate.insufficient_balance_msg(
                bet_price, balance, strategy_name
            )
            logger.info(get_template.get("message"))

            Notification.send_mail(self.data.get_value("email"), get_template)
            Utils.close_game(self.driver, self.data)

    def check_for_profit(self):
        take_profit = self.data.get_int_value("takeProfit")
        if take_profit != 0:
            start_cash = (
                self.data.get_int_value(DataConfigState.StartCash.value) + take_profit
            )

            if self.get_account_balance >= start_cash:
                profit_made = self.get_account_balance - start_cash
                # Generate message template for take profit
                get_template = MessageTemplate.take_profit_msg(profit_made)
                logger.info(get_template.get("message"))

                Notification.send_mail(self.data.get_value("email"), get_template)
                Utils.close_game(self.driver, self.data)

    def check_for_loss(self):
        pass

    def check_finance(self):
        self.check_for_loss()
        self.check_for_profit()

    @property
    def get_list(self):
        while True:
            my_list = [
                int(i.text)
                for i in self.driver.find_elements(
                    By.CLASS_NAME,
                    "colours__item",
                )[:3]
                if i.text
            ]

            print("get list", my_list)
            if len(my_list) == 3:
                return my_list

            time.sleep(2)

    def _enforce_check_time(self):
        while True:
            # Get the current time
            current_time = self.get_time
            print(current_time, "check for current time")
            # Check if the current time is within the desired range (35 to 45 minutes)
            if 10 <= current_time <= 40:
                print("Current time is within the desired range.")
                break
            time.sleep(3)

    def get_draw_result(self):
        draw_numbers = self.get_draw_numbers()

        if self.last_draw == draw_numbers:
            return self.result_from_stats_page()

        self.last_draw = draw_numbers
        return self.get_draw_colors()

    def get_draw_numbers(self):
        ball_elements = self.driver.find_elements(By.CLASS_NAME, "ball__holder")[0]
        ball_value = ball_elements.find_elements(By.CLASS_NAME, "ball-value")
        return [i.text for i in ball_value]

    def get_draw_colors(self):
        color_frequency = {"blue": 0, "green": 0, "red": 0}

        ball_elements = self.driver.find_elements(By.CLASS_NAME, "ball__holder")[0]
        ball_color = ball_elements.find_elements(By.CLASS_NAME, "ball")

        colors = [i.get_attribute("class").split("-")[-1] for i in ball_color]

        for color in colors:
            color_and_its_freq = color_frequency.get(color)
            if color_and_its_freq != None:
                color_frequency[color] += 1

        return color_frequency

    def result_from_stats_page(self, index=0):

        # self._enforce_check_time()

        self.wait.until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.modal__body"))
        )

        self.wait.until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.congratz__txt"))
        )

        self.driver.find_element(By.CSS_SELECTOR, ".stats__toggle").click()

        time.sleep(4)

        my_list = self.get_list

        paginated_list = list(Utils.paginate_list(my_list))
        self.driver.find_element(By.CSS_SELECTOR, ".stats__toggle").click()
        return dict(zip(["red", "green", "blue"], paginated_list[index]))


class BallUtils(GameUtils):
    def check_draw_for_draw(self, color_frequency):
        stringified_frequency = "".join(map(str, sorted(color_frequency.values())))
        if stringified_frequency in ["122", "222", "033"]:
            return True
        return False

    def check_draw_for_33draw(self, color_frequency):
        stringified_frequency = "".join(map(str, sorted(color_frequency.values())))
        if stringified_frequency == "033":
            return True
        return False

    def check_single_zero(self, color_frequency):
        stringified_frequency = "".join(map(str, sorted(color_frequency.values())))
        if "00" in stringified_frequency:
            return False
        elif "0" in stringified_frequency:
            return True
        return False

    def check_draw_for_winning_color(self, color_frequency):
        # Find the key with the highest value
        if not self.check_draw_for_draw(color_frequency):
            max_key = max(color_frequency, key=color_frequency.get)
            return max_key
        return None

    def check_draw_for_4_color(self, color_frequency, colors):
        for color in colors:
            if color_frequency.get(color) >= 4:
                return True
        return False


class DataManager:
    def __init__(self, filename, default_data: dict = {}):
        self.filename = filename
        self.data = {}
        self.load_from_json_file()

        if default_data and self.data == {}:
            self.data = default_data

    def get_value(self, key, default=None):
        return self.data.get(key) or default

    def update_value(self, key, value):
        self.data[key] = value
        self.save_to_json_file()

    def update_list_value(self, key, value):
        val = self.data.get(key) or []
        val.append(value)
        self.data[key] = val
        self.save_to_json_file()

    def increment_value_by(self, key, increment=1):
        value = self.get_int_value(key)
        if isinstance(value, int):
            self.data[key] = value + increment
            self.save_to_json_file()
            return
        raise ValueError("You can only increment type int")

    def get_int_value(self, key, default=0):
        value = self.get_value(key)
        if value:
            return int(value)
        return default

    def get_float_value(self, key, default=0):
        value = self.get_value(key)
        if value:
            return float(value)
        return default

    def save_to_json_file(self):
        with open(self.filename, "w") as file:
            json.dump(self.data, file, indent=2)

    def load_from_json_file(self):
        try:
            with open(self.filename, "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            with open(self.filename, "w") as file:
                json.dump(self.data, file, indent=2)


class StateController:
    def __init__(self, gameState: DataManager):
        self.gameState = gameState

    def save_state(self):
        self.gameState.increment_value_by(GameStateType.TotalTimesRun.value)

    def resetCampaignState(self):
        self.gameState.update_value(GameStateType.CampaignRun.value, 0)


class Utils:
    @staticmethod
    def ask_for_number(question):
        choice = ""
        while choice == "":
            num_input = input(question)
            if num_input.isdecimal():
                choice = int(num_input)
                return choice

    @staticmethod
    def ask_for_float(question):
        choice = ""
        while choice == "":
            try:
                return float(input(question))
            except:
                pass

    @staticmethod
    def ask_for_bool(question):
        while True:
            _input = input(question)
            if _input.lower() in ["1", "yes", "y"]:
                return True
            elif _input.lower() in ["2", "no", "n"]:
                return False
            else:
                print("++++++++++++++++++++\ninvalid choice\n++++++++++++++++++++")

    @staticmethod
    def ask_for_input_range(question, min: int, max: int):
        while True:
            if not isinstance(min, int) or not isinstance(max, int):
                print("Numbers only")
            try:
                no = int(input(question))
                if no in range(min, max):
                    return no
                else:
                    print(f"Only numbers from {min} - {max} allowed")
            except:
                print(f"Enter numbers only from {min} - {max}")

    @staticmethod
    def ask_for_input(question, max_choice):
        choice = ""
        while choice == "":
            num_input = input(question)
            if num_input.isdecimal():
                choice = int(num_input)
                if choice <= max_choice:
                    return choice

                print(
                    "++++++++++++++++++++\nyour choice is out of bound\n++++++++++++++++++++"
                )
                choice = ""
            print("++++++++++++++++++++\ninvalid choice\n++++++++++++++++++++")

    @staticmethod
    def array_vertical(array_2d, num_range):
        final = []
        for k in range(num_range):
            for j in array_2d:
                try:
                    final[k] += str(j[k])
                except Exception:
                    final.append(str(j[k]))
        return final

    @staticmethod
    def array_remove(array_2d, remove_index):
        for array in array_2d:
            remove_data = array[remove_index]
            if len(remove_data) > 1:
                array.remove(remove_data)
        return array_2d

    @staticmethod
    def paginate_list(input_list, page_size=3):
        """Paginate a list into groups of given size."""
        for i in range(0, len(input_list), page_size):
            yield input_list[i : i + page_size]

    @staticmethod
    def find_highest(array: list[int], num: int):
        highest_array = []
        for i, arr in enumerate(array):
            if arr.isdecimal():
                if isinstance(arr, str):
                    arr = int(arr)
                    if arr > num:
                        highest_array.append(i)

        return highest_array

    @staticmethod
    def get_keys_by_value(dictionary, target_value):
        keys_list = []
        for key, value in dictionary.items():
            if value == target_value:
                keys_list.append(key)
        return keys_list

    @staticmethod
    def calculate_martingale_limit(stake, m_p, m_l_n):
        stake = int(stake)
        for i in range(int(m_l_n)):
            stake = stake * m_p
        return stake

    @staticmethod
    def get_game_states():
        filenames = []

        for filename in os.listdir():
            if filename.lower().endswith("gamestate.json"):
                filenames.append(filename)

        return filenames

    @staticmethod
    def reinitialize_game_state(data: DataManager):
        for game_state in Utils.get_game_states():
            data_manager = DataManager(game_state)
            data_manager.update_value("isGamePlayed", False)
            data_manager.update_value("CampaignRun", 0)
            data_manager.update_value("gameLost", 0)

            if data_manager.get_value("stake"):
                data_manager.update_value("stake", data.get_int_value("stake"))

            if data_manager.get_value("playedGames"):
                data_manager.update_value("playedGames", [])

    @staticmethod
    def close_game_delete_state(driver, data):
        Utils.reinitialize_game_state(data)
        driver.close()
        sys.exit()

    @staticmethod
    def close_game(driver, data):
        driver.close()
        sys.exit()
