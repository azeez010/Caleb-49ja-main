from gameStates import ButtonLabels, GameStateType
from strategy.baseStategy import BaseStrategy
from gameUtils import Utils
from gameNotification import Notification, MessageTemplate

from gameLogger import logger


class DoubleRainbowBetStrategy(BaseStrategy):
    strategy_name: str = "play double rainbow color on everyhand"

    rainbow_colors = [["red", "draw"], ["blue", "green"]]

    def balls(self, draws: dict = {}):
        self.gameActions.click_on_link_text(ButtonLabels.TotalColor.value)

        stake = self.get_stake

        color_index = self.gameState.get_int_value(
            GameStateType.CampaignRun.value
        ) % len(self.rainbow_colors)

        colors = self.rainbow_colors[color_index]

        # Reset played color
        self.gameState.update_value("playedGames", [])
        # default is played to False b4 playing
        self.gameState.update_value("isGamePlayed", False)

        for color in colors:
            if self.gameActions.play_totalcolor_game(color, stake):
                self.counter += 1
                logger.info(
                    f"{self.strategy_name}({color}) played {self.counter} times"
                )
                self.gameState.update_list_value("playedGames", color)
                self.gameState.update_value("isGamePlayed", True)

    def check_win_and_update_state(self, draws):
        if self.gameState.get_value("isGamePlayed"):
            gamesPlayed = self.gameState.get_value("playedGames")
            self._check_draw_and_winning_color(gamesPlayed, draws)

    def _check_draw_and_winning_color(self, gamesPlayed, draws):
        if "draw" in gamesPlayed:
            is_draw = self.ballUtils.check_draw_for_draw(draws)

            if is_draw:
                self.game_won_state_update()
            else:
                self._check_winning_color(draws, gamesPlayed)
        else:
            self._check_winning_color(draws, gamesPlayed)

    def _check_winning_color(self, draws, gamesPlayed):
        winning_color = self.ballUtils.check_draw_for_winning_color(draws)

        if winning_color in gamesPlayed:
            self.game_won_state_update()
        else:
            self.game_lost_state_update()
