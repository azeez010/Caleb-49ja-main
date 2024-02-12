from gameUtils import DataManager
from gameStates import BotStrategyType, BotStrategyStakeName
from strategy.drawStrategy import DrawStrategy
from strategy.drawBlackBetStrategy import DrawBlackBetStrategy
from strategy.fourPlusBetStrategy import FourPlusOnZeroColorBetStrategy
from strategy.zeroColorWinningStrategy import ZeroColorWinningStrategy


class Strategy:
    @staticmethod
    def get_stake_name(strategy_stake: int):
        strategy_map = {
            BotStrategyType.DrawBlackBetStrategy.value: BotStrategyStakeName.DrawBlackBetStrategy.value,
            BotStrategyType.FourPlusOnZeroColorBetStrategy.value: BotStrategyStakeName.FourPlusOnZeroColorBetStrategy.value,
            BotStrategyType.ZeroColorWinningStrategy.value: BotStrategyStakeName.ZeroColorWinningStrategy.value,
        }
        return strategy_map[strategy_stake]

    @staticmethod
    def get_strategies(driver, data: DataManager):
        strategy_instances = []
        algorithms = data.get_value("bot_algorithm")

        for algorithm in algorithms:
            strategy_instances.append(Strategy.strategy(algorithm, driver, data))

        return strategy_instances

    @staticmethod
    def strategy(algorithm: int, driver, data: DataManager):
        if algorithm == BotStrategyType.DrawStrategy.value:
            return DrawStrategy(driver, data, DataManager("drawColorGameState.json"))
        elif algorithm == BotStrategyType.DrawBlackBetStrategy.value:
            stakes = DataManager("stakes.json").get_value(
                Strategy.get_stake_name(BotStrategyType.DrawBlackBetStrategy.value)
            )
            return DrawBlackBetStrategy(
                driver, data, DataManager("drawBlackBetGameState.json"), stakes
            )
        elif algorithm == BotStrategyType.FourPlusOnZeroColorBetStrategy.value:
            stakes = DataManager("stakes.json").get_value(
                Strategy.get_stake_name(
                    BotStrategyType.FourPlusOnZeroColorBetStrategy.value
                )
            )
            return FourPlusOnZeroColorBetStrategy(
                driver, data, DataManager("fourPlusOnZeroColorGameState.json"), stakes
            )
        elif algorithm == BotStrategyType.ZeroColorWinningStrategy.value:
            stakes = DataManager("stakes.json").get_value(
                Strategy.get_stake_name(BotStrategyType.ZeroColorWinningStrategy.value)
            )
            return ZeroColorWinningStrategy(
                driver, data, DataManager("ZeroColorWinningGameState.json"), stakes
            )
