from gameStates import ButtonLabels
from gameUtils import Utils
from strategy.baseStategy import BaseStrategy
from gameStates import GameStateType
from gameNotification import Notification, MessageTemplate


class DrawStrategy(BaseStrategy):
    @property
    def _get_stake(self):
        stake = self.gameState.get_int_value("stake")
        if not stake:
            stake = self.data.get_int_value("stake")
        return stake

    @property
    def get_stake(self):
        stake = self._get_stake

        if self.gameState.get_int_value(
            GameStateType.CampaignRun.value
        ) >= self.data.get_int_value("martingaleLimit"):
            # Generate message template
            get_template = MessageTemplate.martingale_limit_msg(
                self.data.get_int_value("martingaleLimit")
            )
            print(get_template.get("message"))

            Notification.send_mail(self.data.get_value("email"), get_template)
            Utils.close_game(self.driver, self.data)

        if self.gameState.get_value("gameLost"):
            stake *= self.data.get_float_value("martingale", 1)
            stake = int(round(stake))
            self.gameState.update_value("stake", stake)
        else:
            stake = self.data.get_int_value("stake")
            self.gameState.update_value("stake", stake)

        return stake

    def balls(self):
        self.gameActions.click_on_link_text(ButtonLabels.TotalColor.value)

        # if self.draw_33_algorithm_check:
        colors = [
            "red",
            "green",
        ]  # Utils.get_keys_by_value(self.ballUtils.get_draw_colors(), 3)
        stake = self.get_stake

        # Check Balance for if the stake would be enough for betting
        self.gameLogic.check_balance(len(colors), stake)

        if len(colors) == 2:
            for color in colors:
                self.gameActions.play_totalcolor_game(color, stake)

            self.gameState.update_value("playedGames", colors)
            self.gameState.update_value("isGamePlayed", True)
            return

        self.gameState.update_value("isGamePlayed", False)

    def check_win_and_update_state(self):
        print(self.gameState.get_value("isGamePlayed"))
        if self.gameState.get_value("isGamePlayed"):
            draws = self.ballUtils.get_draw_colors()
            winning_color = self.ballUtils.check_draw_for_winning_color(draws)

            gamesPlayed = self.gameState.get_value("playedGames")

            print(f"{draws=} {winning_color=} {gamesPlayed=}")

            if winning_color in gamesPlayed:
                self.game_won_state_update()
            else:
                self.game_lost_state_update()