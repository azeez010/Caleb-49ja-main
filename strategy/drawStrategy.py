from gameStates import ButtonLabels
from gameUtils import Utils
from strategy.baseStategy import BaseStrategy
from gameStates import GameStateType
from gameNotification import Notification, MessageTemplate
from gameLogger import logger


class DrawStrategy(BaseStrategy):
    strategy_name: str = (
        "play 2 total winning color on 3/3 draw strategy with martingale"
    )

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
            logger.info(get_template.get("message"))

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

    def balls(self, draws: dict = {}):
        self.gameActions.click_on_link_text(ButtonLabels.TotalColor.value)

        if self.draw_33_algorithm_check(draws):

            colors = Utils.get_keys_by_value(draws, 3)
            stake = self.get_stake

            # Check Balance for if the stake would be enough for betting
            self.gameLogic.check_balance(len(colors), stake, self.strategy_name)

            self.gameState.update_value("playedGames", [])
            self.gameState.update_value("isGamePlayed", False)

            if len(colors) == 2:
                for color in colors:
                    if self.gameActions.play_totalcolor_game(color, stake):
                        self.counter += 1
                        logger.info(f"{self.strategy_name} played {self.counter} times")
                        self.gameState.update_list_value("playedGames", color)
                        self.gameState.update_value("isGamePlayed", True)
