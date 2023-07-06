from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, EmailStr, constr, Field, validator, root_validator
from typing import Dict, Optional, List, Union

from backend.db.base import Adjustment
from backend.services.modules_mock_data import BULLISH, BEARISH
from backend.settings.config import settings

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS

AVAILABLE_MOMENTUM = [BULLISH, BEARISH]


class BuySell(BaseModel):
    sell: str
    buy: str


class AssetExtraDataModel(BaseModel):
    current_share: int = None
    position: int = None
    type_asset: str = None

    class Config:
        orm_mode = False
        schema_extra = {
            "example": {
                "current_share": 500,
                "position": 10,
                'type_asset': "AUD"
            }
        }

    @validator('type_asset', pre=False, always=False)
    def check_type_asset(cls, asset_type):
        if asset_type.strip() not in AVAILABLE_ASSETS:
            raise ValueError(f'asset type should be  {", ".join(AVAILABLE_ASSETS)}')
        return asset_type.strip()


class AssetModel(BaseModel):
    open: float = None
    high: float = None
    low: float = None
    close: float = None
    adjusted_close: float = None
    volume: float = None
    date: str = None
    buy_sell: Union[list] = None
    buy_sell_percent: Union[dict] = None
    levels_crossed: Union[list] = None
    trend_indicator: float = None
    trend_values: Union[dict] = None
    trend_length: float = None
    trend_percent: float = None
    momentum: str = None
    timing: float = None
    adjustment_ids: Union[dict] = None
    position: int = None

    def get_fields_name(self, fields="__all"):
        keys = list(self.dict().keys())
        if fields == "__all":
            return keys
        if fields == '__for_changes__':
            return [
                'open', 'high', 'low', 'close', 'adjusted_close',
                'volume', 'buy_sell', 'levels_crossed',
                'trend_indicator', 'trend_length', 'trend_percent',
                'momentum', 'timing', 'trend_values.0', 'trend_values.3',
                'position'
            ] \
                # + ['buy_sell_percent' , 'trend_values']

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "open": 285.15,
                "high": 292.36,
                "low": 267.94,
                "close": 512,
                "adjustment_ids": {
                    "adj_id": {
                        "open": 100,
                        "high": 200,
                    },
                    "adj_id_1": {
                        "open": 10,
                        "high": 20,
                        "low": 30,
                        "close": 40,
                    }

                },
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
                "momentum": f"{BEARISH} or {BULLISH}",

                "timing": 42,
                "trend_indicator": 300,
                "trend_length": 17,
                "trend_percent": 262,
                "trend_values": {
                    "0": 245.1,
                    "3": 320.55
                },
                "position": 1
            }}

    @validator('momentum', pre=False, always=False)
    def check_momentum(cls, momentum):
        if momentum:
            if momentum.strip() not in AVAILABLE_MOMENTUM:
                raise ValueError(f'momentum should be  {" or ".join(AVAILABLE_MOMENTUM)}')
            return momentum.strip()
        return ''


class ForceUpdateImport(BaseModel):
    records: Union[dict] = None
    type_asset: str = None
    period: str = None
