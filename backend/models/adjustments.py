from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, Field, validator, root_validator
from typing import Dict, Optional, List, Union
from backend.db.base import Adjustment
from backend.settings.config import settings

AVAILABLE_ASSETS = [data[0] for data in settings.AVAILABLE_ASSETS]


class AdjustmentModelMixin(BaseModel):
    @validator('name', check_fields=False)
    def check_name(cls, name):
        if not name: return ''
        clean_name = name.strip()
        item = Adjustment.find_one({'name': clean_name})
        if item:
            raise ValueError(f'Adjustment already exists with name "{clean_name}"')
        return clean_name

    @validator('assets', each_item=True, check_fields=False)
    def check_assets(cls, asset):
        if asset not in AVAILABLE_ASSETS:
            raise ValueError(f'{asset} is not available. Should be : {AVAILABLE_ASSETS}')
        return asset



class AdjustmentModel(AdjustmentModelMixin):
    name: str
    buy_sell_percent: Union[dict] = {}
    trend_values: Union[dict] = {}
    assets: List[str] = []

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "name": "Name of Table",
                "buy_sell_percent": {
                    'buy_plus': 1,
                    'sell_minus': 1,
                },
                "trend_values": {
                    "1": 10,
                    "2": 90
                },
                "assets": ["USD", 'AUD']
            }
        }
    @validator('buy_sell_percent', pre=False, always=True)
    def check_buy_sell_percent(cls, buy_sell_percent):
        for k, v in buy_sell_percent.items():
            if v <= 0:
                raise ValueError(f'{k} can not be negative or zero')
        return buy_sell_percent

    @validator('trend_values', pre=False, always=True)
    def check_trend_values(cls, trend_values):
        if not trend_values:
            raise ValueError('Trend Values field is required')
        AVAILABLE_KEYS: list[str] = ['1', '2']
        MAX_VALUE: int = 100
        payload_keys = trend_values.keys()
        for key in AVAILABLE_KEYS:
            if key not in payload_keys:
                raise ValueError(f'Missing key "{key}". Should be {" , ".join(AVAILABLE_KEYS)}')
        assert MAX_VALUE == sum(trend_values.values()), f'Trend Values: sum of values should be {MAX_VALUE}'
        return trend_values

class AdjustmentUpdateModel(BaseModel):
    name: str = None
    assets: List[str] = []
    buy_sell_percent: Union[dict] = {}
    trend_values: Union[dict] = {}

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "name": "Name of Table",
                "assets": ["USD", 'AUD'],
                "buy_sell_percent": {
                    'buy_plus': 1,
                    'sell_minus': 1,
                },
                "trend_values": {
                    "1": 10,
                    "2": 90
                }
            }
        }
