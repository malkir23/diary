import pymongo
import requests
import datetime
from copy import deepcopy

from app.services.mongo import MongoService
from app.settings.config import settings
from app.db.base import Data, Config
import random
import time
from app.services.email import EmailService
import asyncio

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD
ENDPOINT_SCRAPING = settings.ENDPOINT_SCRAPING


def get_last_time_query(period):
    last_date_for_period_asset = []
    for type_asset in AVAILABLE_ASSETS:
        filter_fields = {"period": period, "type_asset": type_asset}
        result = list(
            Data.find(filter_fields).sort([("date", pymongo.DESCENDING)]).limit(1)
        )
        if result:
            date_string = result[0].get("date")
            if date_string:
                str_date = date_string.strftime("%Y-%m-%d")
                last_date_for_period_asset.append(
                    {
                        "type_asset": type_asset,
                        "period": period,
                        "date": str_date,
                        "type": "schedule",
                        "last_modified": datetime.datetime.now(),
                    }
                )
    else:
        Config.insert_many(last_date_for_period_asset)


def get_last_date_params(period, type_asset):
    filter_fields_for_last_record = {
        "type_asset": type_asset,
        "period": period,
        "type": "schedule",
    }
    last_result = list(
        Config.find(filter_fields_for_last_record)
        .sort([("last_modified", pymongo.DESCENDING)])
        .limit(1)
    )
    date_filter_string = ""
    if last_result:
        last_result = last_result[0]
        date_from = last_result.get("date", "")
        date_obj = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        next_day = date_obj + datetime.timedelta(
            days=1
        )  # get next date for each of queries # TODO: check if api returned valid data by date
        date_from = datetime.datetime.strftime(next_day, "%Y-%m-%d")
        date_to = datetime.datetime.now().strftime("%Y-%m-%d")
        date_filter_string = f"&from={date_from}&to={date_to}"
    return date_filter_string


def get_data_from_api(period, try_count:int=1, assets:list=deepcopy(AVAILABLE_ASSETS)):
    if try_count == 3:
        message = f"Can`t load data for {', '.join(assets)}"
        asyncio.run(EmailService.error_email("", message))

    main_result = []
    last_date_for_period_asset = []
    try_count += 1

    for type_asset in assets.copy():
        dates_list = []
        date_filter_string = get_last_date_params(period=period, type_asset=type_asset)
        try:
            result = requests.get(
                ENDPOINT_SCRAPING.format(type_asset=type_asset, period=period)
                + date_filter_string
            ).json()
            for r in result:
                date_original = r["date"]
                r["date"] = MongoService.string_to_date_mongo(r["date"])
                r["type_asset"] = type_asset
                r["period"] = period
                dates_list.append(date_original)
            max_date = max(dates_list)
            last_date_for_period_asset.append(
                {
                    "type_asset": type_asset,
                    "period": period,
                    "date": max_date,
                    "type": "schedule",
                    "last_modified": datetime.datetime.now(),
                }
            )
        except Exception as e:
            print(type(e), e)
        else:
            assets.remove(type_asset)
            main_result += result

    if not main_result:
        time.sleep(1)
        get_data_from_api(period, try_count, assets)

    Data.insert_many(main_result)

    if last_date_for_period_asset:
        Config.insert_many(last_date_for_period_asset)


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
