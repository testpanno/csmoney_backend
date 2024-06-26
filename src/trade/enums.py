from enum import Enum

class ETradeStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class ETradeType(Enum):
    TRADE = "trade"
    BUY = "buy"
    SELL = "sell"
    
class EGame(Enum):
    CS2 = "cs2"
    CSGO = "csgo"