from datetime import datetime
from backend.services.modules_mock_data import BUY_X, BUY_2X, SELL_X, \
    BOTTOM, TOP, MID, BEARISH, BULLISH, N_A, SELL_ENTIRE_POSITION

template_asset = {
  "open": 285.15,
  "high": 292.36,
  "low": 267.94,
  "close": 512,
  "adjusted_close": 0.1654,
  "volume": 1583149,
  "buy_sell": [
    {
      "buy": 295.3,
      "sell": 183.01,
      "sort_key": 0
    },
    {
      "sell": 194.3,
      "buy": 296.8,
      "sort_key": 1
    }
  ],
  "levels_crossed": [
    {
      "buy": 248.8,
      "sell": 509,
      "sort_key": 0
    },
    {
      "sell": 412.23,
      "buy": 300,
      "sort_key": 1
    }
  ],
  "momentum": "BEARISH",
  "timing": 42,
  "trend_indicator": 300,
  "trend_length": 17,
  "trend_percent": 262,
  "trend_values": {
    "0": 100,
    "3": 200
  }
}

expected_result = {
    "Module A": True,
    "Module B": True,
    "Module C": True,
    "Module D": N_A,
    "Module E": BUY_X,
    "Module F": N_A,
    "Module G": N_A,
    "Module H": BUY_2X,
    "Module I": BUY_X,
    "Module J": N_A,
    "Module K": BUY_X,
    "Module L": N_A,
    "Module M": N_A,
    "Module N": N_A,
    "Module O": N_A,
}

template_adjustment = {
  "name": "basic",
  "buy_sell_percent": {
    "buy_plus": 1,
    "sell_minus": 1
  },
  "trend_values": {
    "1": 10,
    "2": 90
  },
  "assets": [
    "USD",
    "GBP",
    "EUR",
    "CHF",
    "JPY",
    "AUD",
    "CNY",
    "BTC",
    "SPY",
    "DIA",
    "QQQ",
    "TLT",
    "VNQ",
    "GLD",
    "SLV",
    "PDBC",
    "OIL",
    "OIH",
    "FXI",
    "INDA",
    "EWY",
    "EWJ",
    "EEM"
  ]
}

periods = ("m", "w")
