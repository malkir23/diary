import datetime
import re
from enum import Enum
from functools import reduce

from app.db.base import Logs, Adjustment
from app.settings.config import settings
from fastapi import BackgroundTasks

from dataclasses import dataclass, asdict

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD


@dataclass
class TYPES_LOGS:
    ASSET: str = "asset"
    ADJUSTMENT: str = "adjustment"
    GET_ASSETS_FROM_API: str = "get_assets_from_api"
    USERS: str = "users"
    ASSET_DATA: str = "asset_data"


class LogsService:
    """
    type: ['asset' , 'adjustment' , 'get_assets_from_api', 'users']
    actions: ["delete" , 'update' , 'create']
    """

    ACTIONS = ["delete", "update", "create"]
    TYPES_LOGS = list(asdict(TYPES_LOGS()).values())

    ATTRIBUTE_ASSET_FIELDS = [
        "open",
        "close",
        "high",
        "low",
        "adjusted_close",
        "volume",
        "buy_sell.buy",
        "buy_sell.sell",
        "levels_crossed.buy",
        "levels_crossed.sell",
        "momentum",
        "timing",
        "trend_indicator",
        "trend_length",
        "trend_percent",
        "trend_values.0",
        "trend_values.3",
    ]

    ADJUSTMENT_IDS_KEY = 'adjustment_ids'

    def deep_get(self, dictionary, keys, default=None):
        if "trend_values" in keys:
            return dictionary.get(keys)

        empty_template = [] if isinstance(dictionary.get(keys), list) else ""
        return (
            reduce(
                lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
                keys.split("."),
                dictionary,
            )
            or dictionary.get(keys)
            or empty_template
            if dictionary.get(keys) is not False
            else False
        )

    def get_fields_different(
            self,
            before_object,
            after_object,
            fields,
            specific_field=None,
            order=None,
            type_=None,
            adj_map=None,
    ):
        if not fields or len(fields) == 0:
            raise Exception("Wrong fields count")

        changes = []
        for field in fields:
            before = self.deep_get(before_object, field, "")
            after = self.deep_get(after_object, field, "")

            if before is None and after is None: continue

            match type_:
                case TYPES_LOGS.ASSET:
                    empty_value_for_list_field = [
                        {"buy": None, "sell": None, "sort_key": order}
                    ]

                    if field in ["buy_sell", "levels_crossed"]:
                        len_after = len(after)
                        len_before = len(before)

                        if len_before < len_after:
                            delta = len_after - len_before
                            before += empty_value_for_list_field * delta

                        if len_after < len_before:
                            delta = len_before - len_after
                            after += empty_value_for_list_field * delta

                        for before_, after_ in zip(before, after):
                            if before_ != after_:
                                result = self.get_fields_different(
                                    before_,
                                    after_,
                                    fields=["buy", "sell"],
                                    specific_field=field,
                                    order=before_.get("sort_key")
                                    or after_.get("sort_key"),
                                    type_=type_,
                                )
                                for elem in result:
                                    for v in ["old_value", "new_value"]:
                                        if elem[v] == [{}]:
                                            elem[v] = None
                                changes += result
                    else:
                        if before != after:
                            attribute = field
                            last_field = ".".join(field.split('.')[:2])
                            if LogsService.ADJUSTMENT_IDS_KEY in field and type_ == 'asset':
                                attribute = field.replace(last_field, adj_map.get(field.split('.')[1] , 'unknown adjustment'))

                            change_dict = {
                                "attribute": attribute
                                if not specific_field
                                else f"{specific_field}.{field}"
                            }
                            for name_attr, ch in {
                                "old_value": before,
                                "new_value": after,
                            }.items():
                                if isinstance(ch, list):
                                    if {} in ch:
                                        change_dict[name_attr] = None
                                else:
                                    change_dict[name_attr] = ch
                            if order is not None:
                                change_dict["sort_key"] = order
                            changes.append(change_dict)
                case TYPES_LOGS.ADJUSTMENT | TYPES_LOGS.ASSET_DATA:
                    if before != after:
                        changes.append(
                            dict(attribute=field, old_value=before, new_value=after)
                        )

                case TYPES_LOGS.USERS:
                    if before != after:
                        user_change = {
                            "attribute": field,
                            "old_value": before,
                            "new_value": after,
                        }
                        changes.append(user_change)

        return changes

    # @staticmethod
    def __init__(
            self, before_object, after_object, fields, type_, action, obj, user_id
    ):
        type_asset = obj.get('type_asset' , '')
        results_fields = []
        adj_map = {}
        if type_ == 'asset':
            adjustments = list(Adjustment.find({"assets": {"$in": [type_asset]}}))
            adj_ids = []
            for adj in adjustments:
                adj_id  = str(adj.get('_id'))
                adj_ids.append(adj_id)
                adj_map[adj_id] = adj.get('name')

            fields_simple = ['open', 'close', 'high', 'low']

            for simple_field in fields_simple:
                for adj_id in adj_ids:
                    results_fields.append(f'{LogsService.ADJUSTMENT_IDS_KEY}.{adj_id}.{simple_field}')
        changes = None
        if action != "delete":
            changes = self.get_fields_different(
                before_object, after_object, fields=fields + results_fields, type_=type_, adj_map=adj_map
            )
        # TODO user (who?)
        if action == "update":
            try:
                self.is_valid(type_, action, changes)
            except ValueError as e:
                print('ValueError ' , e)
        self.type_ = type_
        self.action = action
        self.changes = changes
        self.create_at = datetime.datetime.now()
        self.object = obj
        self.user_id = user_id

        self.save()

    __str__ = lambda self: f"{self.changes} {self.type_} {self.action} {self.object}"

    def is_valid(self, type_, action, changes):
        if not changes:
            raise ValueError("No changes.")
        if action not in self.ACTIONS:
            raise ValueError(
                f'{self.action} is not valid. Should be {" ".join(self.ACTIONS)}'
            )
        if type_ not in self.TYPES_LOGS:
            raise ValueError(
                f'{self.type_} is not valid. Should be {" ".join(self.TYPES_LOGS)}'
            )

    def save(self):
        Logs.insert_one(self.__dict__)

    @staticmethod
    def get_asset_filter_logs(type_asset, period, attribute):
        if type_asset and type_asset not in AVAILABLE_ASSETS:
            raise ValueError(f"{type_asset} is not valid.")
        if period and period not in AVAILABLE_PERIOD:
            raise ValueError(f"{period} is not valid")
        if attribute and attribute not in LogsService.ATTRIBUTE_ASSET_FIELDS:
            raise ValueError(f"{attribute} is not valid")

        filter_fields = {}
        if type_asset:
            filter_fields["object.type_asset"] = type_asset

        if period:
            filter_fields["object.period"] = period

        if attribute:
            filter_fields["changes"] = {"$elemMatch": {"attribute": attribute}}

        return filter_fields
