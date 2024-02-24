from gameStates import ButtonLabels, GameStateType
from strategy.baseStategy import BaseStrategy
from gameUtils import Utils
from gameNotification import Notification, MessageTemplate
from gameLogger import logger


class ZeroColorWinningStrategy(BaseStrategy):
    strategy_name: str = "play winning color on 3/3 draw strategy"

    @property
    def get_stake(self):
        campaign_run = self.gameState.get_int_value(GameStateType.CampaignRun.value)

        if campaign_run >= len(self.stakes):
            message_template = MessageTemplate.stake_plan_exceeded_msg(
                campaign_run, self.strategy_name
            )
            logger.info(message_template.get("message"))

            Notification.send_mail(self.data.get_value("email"), message_template)
            Utils.close_game(self.driver, self.data)

        return round(self.stakes[campaign_run])

    def balls(self, draws: dict = {}):
        self.gameActions.click_on_link_text(ButtonLabels.TotalColor.value)

        stake = self.get_stake

        if self.draw_33_algorithm_check(draws):
            # Check Balance for if the stake would be enough for betting
            colors = Utils.get_keys_by_value(draws, 0)
            self.gameLogic.check_balance(len(colors), stake, self.strategy_name)

            self.gameState.update_value("playedGames", [])
            self.gameState.update_value("isGamePlayed", False)

            for color in colors:
                if self.gameActions.play_totalcolor_game(color, stake):
                    self.gameState.update_list_value("playedGames", color)
                    self.gameState.update_value("isGamePlayed", True)
                    self.counter += 1
                    logger.info(f"{self.strategy_name} played {self.counter} times")
