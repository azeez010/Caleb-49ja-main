import os
from gameUtils import Utils
from stdiomask import getpass
from gameUtils import DataManager


class SelectorBase:
    def menu_length(self, options: dict):
        return len(options.keys())

    def generate_prompt(self, options: dict):
        return "".join([f"{key}) {value}\n" for key, value in options.items()])

    def get_ask_for_input_data(self, options: dict):
        return self.generate_prompt(options), self.menu_length(options)


class GameSelector(SelectorBase):
    menu_data = {
        "1": "To start the bot DEMO ACCOUNT version",
        "2": "To start the bot LIVE ACCOUNT version",
        "3": "Settings",
        "4": "Exit",
    }

    @property
    def menu_function(self):
        return {
            1: self.engine.start_demo,
            2: self.engine.start_real,
            3: Settings(self.engine).menu_setting,
            4: self.engine.close_bot,
        }

    def __init__(self, engine):
        self.engine = engine
        self.menu()

    def menu(self):
        choice = Utils.ask_for_input(*self.get_ask_for_input_data(self.menu_data))
        self.menu_function[choice]()


class Settings(SelectorBase):
    algorithm_options = {
        "1": "3/3 draw, two color play with martinage",
        "2": "3/3 draw, draw color play with stake plan",
        "3": "3/3 draw, play four plus",
        "4": "3/3 draw, play missing color",
        "5": "every hand, play red, draw then blue, green plus martingale",
        "6": "every hand, play red, blue, green +4 plus martingale",
        "7": "exit",
    }

    menu_setting_options = {
        "1": "Change username",
        "2": "Change password",
        "3": "Change default stake",
        "4": "Change bot algorithms",
        "5": "Change martingale",
        "6": "Change take profit",
        "7": "Change martingale limit",
        "8": "Reset strategy state",
        "9": "Change notification email",
        "10": "finish changes",
    }

    @property
    def menu_setting_function(self):
        return {
            1: self.set_username,
            2: self.set_password,
            3: self.set_default_stake,
            4: self.set_bot_algorithm,
            5: self.set_default_martingale,
            6: self.set_take_profit,
            7: self.set_default_martingale_limit,
            8: self.reset_state,
            9: self.set_notification_email,
            10: self.go_back,
        }

    def __init__(self, engine=None):
        self.engine = engine
        self.defaults = {
            "username": "",
            "password": "",
            "stake": "",
            "email": "",
            "bot_algorithm": [],
        }
        self.data = DataManager("conf.json", self.defaults)
        self.init_settings()

    def reset_state(self):
        game_states_option = {}
        game_states_counter = 1

        for filename in Utils.get_game_states():
            game_states_option[game_states_counter] = filename
            game_states_counter += 1

        game_input = Utils.ask_for_input(
            *self.get_ask_for_input_data(game_states_option)
        )
        if game_input:
            os.remove(game_states_option[game_input])

        self.menu_setting()

    def set_username(self):
        username = input(
            "set your bet9ja username, make sure it is correct because you are allowed to set it once in the bot\n"
        )
        self.data.update_value("username", username)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja username to {username} \n++++++++++++++++++++"
        )

    def set_notification_email(self):
        email = input("set your notification email\n")
        self.data.update_value("email", email)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your notification email {email} \n++++++++++++++++++++"
        )

    def set_default_martingale(self):
        martinage = Utils.ask_for_float("Set your martingale\n")
        self.data.update_value("martingale", martinage)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your default martingale\n++++++++++++++++++++"
        )

    def set_default_martingale_limit(self):
        martinage = Utils.ask_for_number("Set your martingale limit\n")
        self.data.update_value("martingaleLimit", martinage)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your default martingale limit\n++++++++++++++++++++"
        )

    def set_take_profit(self):
        take_profit = Utils.ask_for_float("Set your take profit\n")
        self.data.update_value("takeProfit", take_profit)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your take profit\n++++++++++++++++++++"
        )

    def set_stop_loss(self):
        take_profit = Utils.ask_for_float("Set your stop loss\n")
        self.data.update_value("stopLoss", take_profit)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your stop loss\n++++++++++++++++++++"
        )

    def init_set_email(self):
        if not self.data.get_value("email"):
            self.set_notification_email()

    def init_set_username(self):
        if not self.data.get_value("username"):
            self.set_username()

    def init_set_password(self):
        if not self.data.get_value("password"):
            self.set_password()

    def set_password(self):
        password = getpass(prompt="set your bet9ja password \n")
        self.data.update_value("password", password)
        print(
            f"++++++++++++++++++++\ncongratulation!!!!!!!, you have successfully set your bet9ja password \n++++++++++++++++++++"
        )

    def init_set_default_stake(self):
        if not self.data.get_value("stake"):
            self.set_default_stake()

    def set_default_stake(self):
        not_enough_bet = True

        # making sure the bet is more than
        while not_enough_bet:
            bet_value = input(
                "set the amount you want the bot to bet in naira e.g 100, you can always change this in the settings \n"
            )
            if bet_value.isdecimal():
                if int(bet_value) >= 50:
                    self.data.update_value("stake", bet_value)
                    print(
                        f"++++++++++++++++++++\nthe bet price has been successfully set {bet_value}\n++++++++++++++++++++"
                    )
                    not_enough_bet = False
                else:
                    print(
                        "++++++++++++++++++++\nthe least amount a bot can bet is 50\n++++++++++++++++++++"
                    )

            else:
                print(
                    "++++++++++++++++++++\nenter number not alphabets\n++++++++++++++++++++"
                )

    def init_set_bot_algorithm(self):
        if not self.data.get_value("bot_algorithm"):
            self.set_bot_algorithm()

    def set_bot_algorithm(self):
        algorithm_selection = []

        while True:
            print("Set your prefered the bot algorithm\n")
            menu_length = self.menu_length(self.algorithm_options)
            algo_value = Utils.ask_for_input(
                *self.get_ask_for_input_data(self.algorithm_options)
            )
            if algo_value == menu_length and algorithm_selection:
                break

            if algo_value not in algorithm_selection and algo_value != menu_length:
                algorithm_selection.append(algo_value)

            self.data.update_value("bot_algorithm", algorithm_selection)

    def go_back(self):
        GameSelector(self.engine)

    def init_settings(self):
        self.init_set_username()
        self.init_set_password()
        self.init_set_default_stake()
        self.init_set_bot_algorithm()
        self.init_set_email()

    def menu_setting(self):
        choice = Utils.ask_for_input(
            *self.get_ask_for_input_data(self.menu_setting_options)
        )
        self.menu_setting_function[choice]()
        self.menu_setting()
