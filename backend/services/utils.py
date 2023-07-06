from functools import reduce

from backend.db.base import Data, Adjustment
from backend.services.modules import N_A
from backend.settings.config import settings
from fastapi import HTTPException, status
import datetime
import re
from pymongo import InsertOne, UpdateOne

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD

simple_col_numbers = ['open', 'low', 'close', 'high', 'trend_indicator', 'trend_values.0', 'trend_values.3',
                      'trend_length', 'trend_percent', 'timing']


def utc_now(date_format=''):
    now = datetime.datetime.now()
    if not date_format: return now
    return now.strftime(date_format)


def remove_nulls_from_dict(dict_value):
    return {k: v for k, v in dict_value.items() if v is not None}


def deep_get(dictionary, keys, default=None):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split('.'), dictionary)


def get_fields_different(before_object, after_object, fields, specific_field=None, order=None):
    if not fields or len(fields) == 0:
        raise Exception('Wrong fields count')

    changes = []
    for field in fields:
        before = deep_get(before_object, field, '')
        after = deep_get(after_object, field, '')
        if field in ['buy_sell', 'levels_crossed']:
            for before_, after_ in zip(before, after):
                if before_ != after_:
                    result = get_fields_different(before_, after_, fields=['buy', 'sell'], specific_field=field,
                                                  order=before_.get('sort_key'))
                    changes += result
        else:
            if before != after:
                change_dict = dict(attribute=field if not specific_field else f'{specific_field}.{field}',
                                   old_value=before,
                                   new_value=after)
                if order is not None:
                    change_dict['sort_key'] = order
                changes.append(change_dict)

    return changes


def check_period_asset_valid(period, type_asset):
    if period not in AVAILABLE_PERIOD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'period must be "{", ".join(AVAILABLE_PERIOD)}"',
        )
    type_asset_list = [db_value for db_value, api_value in AVAILABLE_ASSETS]
    if type_asset not in type_asset_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"type_asset must be one of {AVAILABLE_ASSETS}",
        )


def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Value not found


def is_number(value):
    if isinstance(value, str):
        # Regex pattern to match integer or float
        pattern = r'^[-+]?[0-9]+(\.[0-9]+)?$'
        return bool(re.match(pattern, value))
    elif isinstance(value, int) or isinstance(value, float):
        return True
    return False


def find_not_null_value(list_of_values):
    result_value = next(filter(lambda x:
                               is_number(x) and
                               x is not None,
                               list_of_values), None)
    return float(result_value) if result_value is not None \
        else print(result_value, 'is not a number')


def compare_list_of_value(first_list, second_list, first_key, second_key):
    zipped_object = list(zip(first_list, second_list))
    result_list = []
    for sort_key, elem in enumerate(zipped_object):
        first_value, second_value = elem
        # if first_value or second_value:
        result_list.append(
            {first_key: first_value, second_key: second_value, "sort_key": sort_key}
        )
    return result_list


def prepare_data_to_db(data):
    result_dict = {}
    for date_key, value in data.items():
        buy_sell_sell_value = value.get('buy_sell.sell', [])
        buy_sell_buy_value = value.get('buy_sell.buy', [])
        level_crossed_sell_value = value.get('levels_crossed.sell', [])
        level_crossed_buy_value = value.get('levels_crossed.buy', [])

        buy_sell_value = compare_list_of_value(buy_sell_sell_value, buy_sell_buy_value,
                                               first_key='sell', second_key='buy')
        levels_crossed_value = compare_list_of_value(level_crossed_sell_value, level_crossed_buy_value,
                                                     first_key='sell', second_key='buy')
        momentum_value = value.get('momentum', [None])[0]

        result_dict[date_key] = {
            'trend_values': {},
        }
        if buy_sell_value:
            result_dict[date_key]['buy_sell'] = buy_sell_value

        if levels_crossed_value:
            result_dict[date_key]['levels_crossed'] = levels_crossed_value

        if momentum_value:
            result_dict[date_key]['momentum'] = momentum_value

        for db_col, db_value in value.items():
            if db_col in simple_col_numbers:
                if 'trend_values' in db_col:
                    split_trend_values = db_col.split('.')[-1]
                    trend_values_v = find_not_null_value(db_value)
                    if not trend_values_v: continue

                    if split_trend_values not in result_dict[date_key].get('trend_values', {}):
                        result_dict[date_key]['trend_values'][split_trend_values] = trend_values_v
                    else:
                        result_dict[date_key]['trend_values'].update(
                            {split_trend_values: trend_values_v}
                        )
                else:
                    part_of_value_asset = find_not_null_value(db_value)
                    if part_of_value_asset:
                        result_dict[date_key][db_col] = part_of_value_asset
    return result_dict


def has_values(asset):
    keys = ['trend_length', 'trend_percent', 'momentum']

    not_empty_buy_sell = False
    not_empty_trend_values = any(list(asset.get('trend_values', {}).values()))
    for dict_key in ['buy_sell', 'levels_crossed']:
        if asset.get(dict_key):
            for v in asset.get(dict_key):  # [{'buy': 1 , 'sell': 2 , "sort_key": 0}]
                buy = v.get('buy', N_A)
                sell = v.get('sell', N_A)
                if (buy is not None and buy != N_A) or (sell is not None and sell != N_A):
                    not_empty_buy_sell = True
                    break
        if not_empty_buy_sell:
            break

    is_not_empty = any([asset.get(key) for key in keys]) or not_empty_buy_sell or not_empty_trend_values

    return is_not_empty


adj_fields = ['open', 'low', 'close', 'high']


def create_fields_by_adj(data, asset=None, is_new=False):
    """
    Args:
        data: asset record
    Returns: {
        "open": 1, if open is not None
        "low": 2, if low is not None
        "close": 3, if close is not None
        "high": 4, if high is not None
    }

    """
    adjustment_relation_fields = {}
    different_fields = []

    if is_new:
        adjustment_relation_fields = {
            adj_f: data.pop(adj_f) for adj_f in adj_fields if data.get(adj_f) is not None
        }
    else:
        for f in adj_fields:
            data_in_db = asset.get(f)
            data_in_file = data.get(f)
            if data_in_db != data_in_file:
                different_fields.append(f)
                adjustment_relation_fields[f] = data_in_file
    return adjustment_relation_fields, different_fields


def update_asset_from_file(type_asset, period, data):
    adj = dict(Adjustment.find_one({'is_default': True}))  # "basic" adjustment for close , open , high , low values
    basic_adj_id = str(adj.get("_id"))
    dates = list(data.keys())
    assets = list(Data.find({'date': {"$in": dates}, 'period': period, 'type_asset': type_asset}))

    assets_date = []
    bulk_operations = []
    conflicts_records = {}
    for asset in assets:
        assets_date.append(asset.get('date'))

        is_asset_with_values = has_values(asset)
        asset_date = asset.get('date')
        update_data = data.get(asset_date)
        new_adjustment_data, different_fields = create_fields_by_adj(update_data, asset=asset)

        for f in different_fields:
            update_data.pop(f)
            # try:
            #
            #
            # except Exception as e:
            #     print(type(e) , e)
            #     print(update_data , f)

        if new_adjustment_data:
            update_data['adjustment_ids'] = {basic_adj_id: new_adjustment_data}

        if not is_asset_with_values:
            """ UPDATE EXISTS RECORD """
            bulk_operations.append(
                UpdateOne({"_id": asset.get('_id')}, {'$set': update_data})
            )
        else:
            """ CONFLICT:  ALREADY EXISTS WITH NON-EMPTY values """
            update_data['period'] = period
            update_data['type_asset'] = type_asset
            conflicts_records[str(asset_date)] = update_data

            print('conflict!')

    if len(assets) < len(dates):
        """ INSERT NEW RECORDS """
        new_dates = [new_date for new_date in set(dates).difference(set(assets_date))]
        for new_date in new_dates:
            new_record = data.get(new_date)
            if new_record:
                adjustment_relation_fields, _ = create_fields_by_adj(new_record, is_new=True)
                new_record['adjustment_ids'] = {basic_adj_id: adjustment_relation_fields}
                new_record['type_asset'] = type_asset
                new_record['period'] = period
                new_record['date'] = new_date

                bulk_operations.append(
                    InsertOne(new_record)
                )

    result_bulk_update = Data.bulk_write(bulk_operations)

    return {
        'has_conflict': bool(len(conflicts_records)),
        'len_conflicts_records': len(conflicts_records),
        'conflicts_records': conflicts_records,
        'matched_count': result_bulk_update.matched_count,
        'inserted_count': result_bulk_update.inserted_count,
        'modified_count': result_bulk_update.modified_count,
        'deleted_count': result_bulk_update.deleted_count,
        'upserted_ids': result_bulk_update.upserted_ids,
    }
