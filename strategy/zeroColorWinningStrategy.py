from gameStates import ButtonLabels, GameStateType
from strategy.baseStategy import BaseStrategy
from gameUtils import Utils
from gameNotification import Notification, MessageTemplate


class ZeroColorWinningStrategy(BaseStrategy):
    strategy_name: str = "play winning color on 3/3 draw strategy"

    @property
    def get_stake(self):
        campaign_run = self.gameState.get_int_value(GameStateType.CampaignRun.value)

        if campaign_run >= len(self.stakes):
            message_template = MessageTemplate.stake_plan_exceeded_msg(
                campaign_run, self.strategy_name
            )
            print(message_template.get("message"))

            Notification.send_mail(self.data.get_value("email"), message_template)
            Utils.close_game(self.driver, self.data)

        return round(self.stakes[campaign_run])

    def balls(self):
        self.gameActions.click_on_link_text(ButtonLabels.TotalColor.value)

        stake = self.get_stake

        if self.draw_33_algorithm_check:
            # Check Balance for if the stake would be enough for betting
            # colors = Utils.get_keys_by_value(self.ballUtils.get_draw_colors(), 0)
            colors = Utils.get_keys_by_value(self.ballUtils.result_from_stats_page(), 0)
            self.gameLogic.check_balance(len(colors), stake, self.strategy_name)

            for color in colors:
                self.gameActions.play_totalcolor_game(color, stake)

                self.gameState.update_value("playedGames", colors)
                self.gameState.update_value("isGamePlayed", True)

                self.counter += 1
                print(f"{self.strategy_name} played {self.counter} times")
                return

        self.gameState.update_value("isGamePlayed", False)
