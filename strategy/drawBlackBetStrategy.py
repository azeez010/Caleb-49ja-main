from gameStates import ButtonLabels, GameStateType
from strategy.baseStategy import BaseStrategy
from gameUtils import Utils
from gameNotification import Notification, MessageTemplate


class DrawBlackBetStrategy(BaseStrategy):
    strategy_name: str = "play draw no winning color on 3/3 draw strategy"

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
            self.gameLogic.check_balance(1, stake, self.strategy_name)
            self.gameActions.play_totalcolor_game("draw", stake)
            self.gameState.update_value("isGamePlayed", True)
            self.counter += 1
            print(f"{self.strategy_name} played {self.counter} times")
            return

        self.gameState.update_value("isGamePlayed", False)

    def check_win_and_update_state(self):
        if self.gameState.get_value("isGamePlayed"):
            draws = self.ballUtils.get_draw_colors()
            is_draw = self.ballUtils.check_draw_for_draw(draws)

            if is_draw:
                self.game_won_state_update()
            else:
                self.game_lost_state_update()
