import pymongo
import requests
import datetime
from copy import deepcopy

from backend.services.mongo import MongoService
from backend.services.utils import utc_now
from backend.settings.config import settings
from backend.db.base import Data, Config
import random
import time
from backend.services.email import EmailService
import asyncio

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD
ENDPOINT_SCRAPING = settings.ENDPOINT_SCRAPING


class Scraping:
    def __init__(self):
        self.main_result = []
        self.last_date_for_period_asset = []
        self.map_period = {"m": 'monthly', 'd': 'daily', 'w': "weekly"}
        self.missing_data_errors = {}
        self.unknown_data_errors = {}

    def fill_data(self):
        for period in self.map_period:
            self.get_data_from_api(period=period)

        self.write_result_to_db()
        self.write_config_schedule()
        self.check_error()

    def write_result_to_db(self):
        if self.main_result:
            Data.insert_many(self.main_result)

    def check_error(self):
        final_message = ''
        format_message = '<br><b>{}</b>:<br> {} '
        if self.missing_data_errors:
            final_message += 'Missing data for'
            for type_asset, messages in self.missing_data_errors.items():
                final_message += format_message.format(type_asset, "\t".join(messages))

        if self.unknown_data_errors:
            final_message += '<br>Unknown errors. Please contact with administrator: <br>'
            for type_asset, messages in self.unknown_data_errors.items():
                final_message += format_message.format(type_asset, "\t".join(messages))

        if final_message:
            asyncio.run(EmailService.error_email("", final_message))

    def write_config_schedule(self):
        if self.last_date_for_period_asset:
            Config.insert_many(self.last_date_for_period_asset)

    def get_data(self, period):
        self.get_data_from_api(period)

        self.write_result_to_db()
        self.write_config_schedule()
        self.check_error()

    def get_last_date_params(self, period, name_for_api):
        filter_fields_for_last_record = {
            "type_asset": name_for_api,
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
            next_day_string = ''
            date_to = datetime.datetime.now().strftime("%Y-%m-%d")
            if date_from:
                print('date_from ' , date_from)
                date = datetime.datetime.strptime(date_from, '%Y-%m-%d')
                next_day = date + datetime.timedelta(days=1)
                next_day_string = next_day.strftime('%Y-%m-%d')
            date_filter_string = f"&from={next_day_string}&to={date_to}"

        return date_filter_string

    def get_data_from_api(self, period, assets: list = deepcopy(AVAILABLE_ASSETS)):
        for type_asset, name_for_api in assets.copy():
            dates_list = []
            kwargs_asset = {"period": period, "name_for_api": name_for_api}
            date_filter_string = self.get_last_date_params(**kwargs_asset)
            try:
                result_data = []
                for _ in range(3):
                    result = requests.get(
                        ENDPOINT_SCRAPING.format(**kwargs_asset)
                        + date_filter_string
                    )
                    if result.status_code != 200:
                        now = utc_now("%Y-%m-%d %H:%M:%S")
                        message = f"Period: <b>{self.map_period[period]}</b> Time: <b>{now}</b><br>"
                        if name_for_api not in self.unknown_data_errors:
                            self.unknown_data_errors[name_for_api] = [message]
                        else:
                            self.unknown_data_errors[name_for_api].append(message)
                        break
                    result_data = result.json()
                    if not result_data: continue

                    for r in result_data:
                        date_original = r["date"]
                        r["date"] = MongoService.string_to_date_mongo(r["date"])
                        r["type_asset"] = type_asset
                        r["period"] = period
                        dates_list.append(date_original)
                    max_date = max(dates_list)
                    self.last_date_for_period_asset.append(
                        {
                            "type_asset": name_for_api,
                            "period": period,
                            "date": max_date,
                            "type": "schedule",
                            "last_modified": datetime.datetime.utcnow(),
                        }
                    )
                    break
                else:
                    now = utc_now("%Y-%m-%d %H:%M:%S")
                    message = f"Period: <b>{self.map_period[period]}</b> Time: <b>{now}</b> <br>"
                    if name_for_api not in self.missing_data_errors:
                        self.missing_data_errors[name_for_api] = [message]
                    else:
                        self.missing_data_errors[name_for_api].append(message)
            except Exception as e:
                print(type(e), e)
            else:
                self.main_result += result_data

