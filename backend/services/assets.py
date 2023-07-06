import requests
from backend.settings.config import settings
from backend.db.base import Data
import random
import copy

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD
ENDPOINT_SCRAPING = settings.ENDPOINT_SCRAPING


def get_data_from_api(period):
    main_result = []
    for type_asset in AVAILABLE_ASSETS:
        result = requests.get(
            ENDPOINT_SCRAPING.format(type_asset=type_asset, period=period)
        )
        main_result += result
    Data.insert_many(main_result)


def generate_random_data():
    main_result = []
    for type_asset in AVAILABLE_ASSETS:
        for period in AVAILABLE_PERIOD:
            # result  = requests.get(ENDPOINT_SCRAPING.format(type_asset=type_asset, period=period))
            main_result += [
                {
                    "date": "2022-01-06",
                    "open": random.uniform(10.5, 75.5),
                    "high": random.uniform(10.5, 75.5),
                    "low": random.uniform(10.5, 75.5),
                    "close": random.uniform(10.5, 75.5),
                    "adjusted_close": random.uniform(10.5, 75.5),
                    "volume": random.randint(10, 300),
                    "type_asset": type_asset,
                    "period": period,
                }
                for _ in range(30)
            ]

    result = Data.insert_many(main_result)


