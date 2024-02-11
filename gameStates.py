from enum import Enum, auto


class BootType(Enum):
    Real = auto()
    Demo = auto()


class BotStrategyType(Enum):
    DrawStrategy = auto()
    DrawBlackBetStrategy = auto()
    FourPlusOnZeroColorBetStrategy = auto()
    ZeroColorWinningStrategy = auto()


class BotStrategyStakeName(Enum):
    DrawStrategy = "draw_stakes"
    FourPlusOnZeroColorBetStrategy = "four_plus_on_zero_color_stakes"
    ZeroColorWinningStrategy = "zero_color_winning_stakes"


class GameStateType(Enum):
    TotalTimesRun = "TotalTimesRun"
    CampaignRun = "CampaignRun"


class ButtonLabels(Enum):
    Rainbow = "Rainbow"
    TotalColor = "Total Colour"


class DataConfigState(Enum):
    StartCash = "StartCash"
