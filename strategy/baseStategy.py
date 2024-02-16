from gameUtils import BallUtils, StateController, DataManager, GameLogic
from gameStates import ButtonLabels, GameStateType
from gameActions import GameActions
from selenium.webdriver import Chrome


class BaseStrategy:
    strategy_name: str = "base strategy"
    counter: int = 0

    def __init__(
        self,
        driver: Chrome,
        data: DataManager,
        gameState: DataManager,
        stakes: list = [],
    ):
        self.driver = driver
        self.data = data
        self.gameState = gameState
        self.stakes = stakes

        self.gameActions = GameActions(self.driver, self.data)
        self.ballUtils = BallUtils(self.driver, self.data)
        self.stateController = StateController(self.gameState)
        self.gameLogic = GameLogic(self.driver, self.data)

        self.init_game_state()

    def init_game_state(self):
        self.gameState.update_value("isGamePlayed", False)

    @property
    def draw_33_algorithm_check(self):
        # color_frequency = self.ballUtils.get_draw_colors()
        color_frequency = self.ballUtils.result_from_stats_page()
        return self.ballUtils.check_draw_for_33draw(color_frequency)

    @property
    def zero_color_algorithm_check(self):
        # color_frequency = self.ballUtils.get_draw_colors()
        color_frequency = self.ballUtils.result_from_stats_page()
        return self.ballUtils.check_single_zero(color_frequency)

    def run(self):
        self.balls()
        self.stateController.save_state()

    def game_won_state_update(self):
        self.gameState.increment_value_by("gamesWon")
        self.gameState.update_value("gameLost", False)
        self.gameState.update_value(GameStateType.CampaignRun.value, 0)

    def game_lost_state_update(self):
        self.gameState.increment_value_by("gamesLost")
        self.gameState.update_value("gameLost", True)
        self.gameState.increment_value_by(GameStateType.CampaignRun.value)

    def check_win_and_update_state(self):
        if self.gameState.get_value("isGamePlayed"):
            # draws = self.ballUtils.get_draw_colors()
            draws = self.ballUtils.result_from_stats_page()
            winning_color = self.ballUtils.check_draw_for_winning_color(draws)

            gamesPlayed = self.gameState.get_value("playedGames")

            if winning_color in gamesPlayed:
                self.game_won_state_update()
            else:
                self.game_lost_state_update()
