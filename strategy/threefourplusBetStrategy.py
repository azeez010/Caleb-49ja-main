from gameStates import ButtonLabels
from strategy.baseStategy import BaseStrategy

from gameLogger import logger


class ThreeFourPlusBetStrategy(BaseStrategy):
    strategy_name: str = "play double rainbow color on everyhand"

    rainbow_colors = ["red", "blue", "green"]

    def balls(self, draws: dict = {}):
        self.gameActions.click_on_link_text(ButtonLabels.Rainbow.value)

        stake = self.get_stake
        colors = self.rainbow_colors

        self.gameLogic.check_balance(len(colors), stake, self.strategy_name)

        self.gameState.update_value("playedGames", [])
        self.gameState.update_value("isGamePlayed", False)

        for color in colors:
            if self.gameActions.play_rainbow_game(color, stake):
                self.counter += 1
                logger.info(
                    f"{self.strategy_name} ({color}) played {self.counter} times"
                )
                self.gameState.update_value("isGamePlayed", True)
                self.gameState.update_list_value("playedGames", color)

    def check_win_and_update_state(self, draws):
        if self.gameState.get_value("isGamePlayed"):
            gamesPlayed = self.gameState.get_value("playedGames")

            if self.ballUtils.check_draw_for_4_color(draws, gamesPlayed):
                self.game_won_state_update()
            else:
                self.game_lost_state_update()
