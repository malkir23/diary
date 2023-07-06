# import pymongo
from datetime import datetime
import calendar
from bson import ObjectId
from backend.services.modules_mock_data import TOP, BOTTOM, MID, BULLISH, BEARISH
from itertools import product

if __name__ != "__main__":
    from fastapi import HTTPException, status
    import pymongo
    from backend.db.base import Data

# 298.55	305.254	358.886	365.59
MODULE_RESULTS = {}
N_A = "N/A"
# ASSET = {
#     'trend_length': 29,
#     'trend_proc': 333,
#     'high': 368.25,
#     'close': 305.05,
#     'buy_sell_percent_1': [
#         {
#             "buy_plus_percent": 56.2,
#             "sell_minus_percent": 233.442,
#             "sort_key": 0
#         },
#         {
#             "buy_plus_percent": 52,
#             "sell_minus_percent": 26.5,
#             "sort_key": 1
#         }
#     ],  # 298.55	305.254	358.886	365.59
#     'levels_crossed': {
#         'sell': 232.40,
#         'buy': 308.555
#     },
#     'trend_indicator': 100,
#     'trend_values': {
#         '0': 298.55,
#         '10': 305.254,
#         '90': 358.886,
#         '100': 365.59
#     },
#     'momentum': 'bearish'
# }
#


import json

ASSET = {
    "_id": ObjectId("6401da9a97f1ecc9eab5b326"),
    "open": 327.57,
    "high": 331.2,
    "low": 326.8,
    "close": 330.44,
    "adjusted_close": 330.44,
    "volume": 3047500.0,
    "type_asset": "DIA",
    "period": "d",
    "buy_sell": [{"buy": 305.5, "sell": 362.65, "sort_key": 0}],
    "buy_sell_percent_1": [
        {"buy_plus_percent": 308.555, "sell_minus_percent": 172.953, "sort_key": 0}
    ],
    "levels_crossed": [{"buy": 308.555, "sell": None, "sort_key": 0}],
    "momentum": BULLISH,
    "trend_indicator": 225.26,
    "trend_values": {"0": 298.55, "10": 305.254, "90": 358.886, "100": 365.59},
    "trend_length": 28.0,
    "trend_percent": 333.0,
    "timing": 36.0,
}

LAST_MONTHLY_ASSET = {
    "buy_sell_percent_1": [
        {"buy_plus_percent": 308.555, "sell_minus_percent": 172.953, "sort_key": 0}
    ],
    "momentum": BULLISH,
}

CHECK_ASSETS_FIELDS = (
    "trend_length", "trend_percent", "position", "buy_sell",
    "trend_values", "trend_indicator", "momentum"
)


class DoesNotExistsDataRecord(Exception):
    pass


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def filter_dicts_by_max_value(dicts, key) -> int | float | str | None:
    if not dicts:
        return
    values = [d[key] for d in dicts if d.get(key)] + [0, 0]

    if N_A in values:
        return N_A

    return max(*values)


operators = {
    ">": float.__gt__,
    "<": float.__lt__,
    "<=": float.__le__,
    ">=": float.__ge__,
    "==": float.__eq__,
}
str_operators = {"==": str.__eq__, "in": list.__contains__}

# list
results = {"yes": True, "no": False}

bool_maps_operator = {"or": bool.__or__, "and": bool.__and__}


def convert_to_float(value):
    try:
        return float(value)
    except ValueError as e:
        pass


def get_answer(obj):
    current_result = None
    use_indexes = []
    previous_connector = ""
    for index, data in obj.items():
        if index in use_indexes:
            continue
        current_val = data["val"]
        try:
            connector = data["connector"]
            previous_connector = connector
            next_data = obj[index + 1]
            bool_function = bool_maps_operator[connector]
            if current_result is None:
                current_result = bool_function(
                    bool(current_val), bool(next_data["val"])
                )
            else:
                current_result = bool_function(current_val, current_result)
        except KeyError as e:
            current_result = bool_maps_operator[previous_connector](
                bool(current_val), bool(current_result)
            )
        else:
            use_indexes += [index, index + 1]

    return current_result


def get_operand_value(operand, module_index, current_asset=ASSET, adj=None):
    value = None
    if isinstance(operand, list):
        value = operand
        return value
    elif operand in current_asset:
        if adj:
            adj_id = str(adj.get('_id'))
            if 'adjustment_ids' in current_asset:
                if adj_id in current_asset['adjustment_ids']:
                    if operand in current_asset['adjustment_ids'][adj_id]:
                        value = current_asset['adjustment_ids'][adj_id][operand]
                    else:
                        value = current_asset[operand]
                else:
                    value = current_asset[operand]
            else:
                value = current_asset[operand]
                if module_index == 4 and value == BEARISH: # for Module E always should be BEARISH
                    value = BULLISH
        else:
            value = current_asset[operand]
    elif isinstance(operand, str) and "." in operand:
        if 'trend_values' in operand:
            trend_values = current_asset.get('trend_values')
            if trend_values is None:
                return
            find_key = operand.split('.')[-1]
            trend_values_0 = trend_values['0']
            trend_values_100 = trend_values['3']
            # if not trend_values_0 and not trend_values_100:
            #     return
            # 53.57 trend_values.0
            #
            # (72.02-53.57)*20/100+53.57=57.26 trend_values.1
            #
            # (72.02-53.57)*80/100+53.57=68.33 trend_values.2
            #
            # 72.02 trend_values.100
            trend_values_1 = adj.get('trend_values', {}).get('1')
            trend_values_2 = adj.get('trend_values', {}).get('2')
            match find_key:
                case '0':
                    value = trend_values_0
                case '3':
                    value = trend_values_100
                case '1':
                    value = (
                                    trend_values_100 - trend_values_0) * trend_values_1 / 100 + trend_values_0  # TODO 20 - adjustment.trend_values.1
                case '2':
                    value = (
                                    trend_values_100 - trend_values_0) * trend_values_2 / 100 + trend_values_0  # TODO 80 - adjustment..trend_values.2

        elif "levels_crossed" in operand and isinstance(
                current_asset.get("levels_crossed"), list
        ):
            list_values = current_asset.get("levels_crossed")
            value = [elem for elem in list_values if elem.get("sort_key") == 0][0].get(
                operand.split(".")[-1]
            )

        else:
            value = safeget(current_asset, *(operand.split(".")))

        if not value:
            return None
    elif isinstance(operand, str) and "module_index_" in operand:
        index_module_result = int(operand.replace("module_index_", ""))
        if index_module_result in MODULE_RESULTS[str(adj['_id'])]:
            if not MODULE_RESULTS[str(adj['_id'])][index_module_result]:
                return N_A
            return MODULE_RESULTS[str(adj['_id'])][index_module_result]
    elif isinstance(operand, str) and "prev_module_rule_index_" in operand:
        index_module_result = int(operand.replace("prev_module_rule_index_", ""))
        prev_module = module_index - 1
        prev_result = MODULE_RESULTS.get(str(adj['_id']))[prev_module]
        if prev_result == index_module_result:
            return {
                "break": True,
                "index_module_result": index_module_result,
            }
    elif isinstance(operand, str) and operand.strip() in [BULLISH, BEARISH]:
        return operand
    elif operand in [MID, BOTTOM, TOP]:
        return operand
    else:
        if operand:
            value = convert_to_float(operand)
    return value


def get_asset_or_value(extra_settings, asset, operand, side_operation="right", adj=None):
    current_asset = None
    value = None
    type_ = extra_settings.get("type")
    if extra_settings and extra_settings.get("operand") == side_operation:
        order = extra_settings.get("order")  # last
        type_asset = asset.get("type_asset")  # change to current asset
        period = extra_settings.get("period")  # m w d
        if period and order and order == 'last' and type_ == 'max':
            current_asset = get_last_m_asset(type_asset, asset.get('date'))

            # except IndexError as e:
            #     raise DoesNotExistsDataRecord('Last monthly record is missing.')

            first_key = operand.split(".")[0]
            find_key = operand.split(".")[-1]

            list_value = current_asset[first_key]
            value = filter_dicts_by_max_value(list_value, find_key)
        elif period and order and order == 'last':
            current_asset = get_last_m_asset(type_asset, asset.get('date'))
        elif order == 'previous':
            filter_fields = {"period": asset.get("period"), "type_asset": type_asset}
            filter_fields['date'] = {"$lt": asset.get('date')}
            current_asset = (
                Data.find(filter_fields)
                .sort([("date", pymongo.DESCENDING)])
                .limit(1)[0]
            )
        else:

            if order and order == "last":

                filter_fields = {"period": asset.get('period'), "type_asset": type_asset}
                if __name__ == "__main__":
                    current_asset = LAST_MONTHLY_ASSET
                else:
                    current_asset = (
                        Data.find(filter_fields)
                        .sort([("date", pymongo.ASCENDING)])
                        .limit(1)[0]
                    )
            elif type_ and type_ == "max":
                is_calculate_field = False
                first_key = operand.split(".")[0]  # levels_crossed || buy_sell_percent_1
                if __name__ == "__main__":
                    current_asset = asset
                    list_value = current_asset.get(first_key)
                else:
                    current_asset = Data.find_one({"_id": ObjectId(str(asset.get("_id")))})
                    find_key = operand.split(".")[-1]

                    try:
                        if first_key in ['buy_sell_percent']:
                            is_calculate_field = True
                            list_value = current_asset.get('buy_sell')
                            if find_key == 'sell_minus':
                                max_values = filter_dicts_by_max_value(list_value, 'sell')
                                value = max_values
                                percent = adj.get('buy_sell_percent', {}).get(find_key)
                                if percent:
                                    if value:
                                        value = value * ((100 - percent) / 100)  # TODO: calculate by adjustment
                            elif find_key == 'buy_plus':
                                value = filter_dicts_by_max_value(list_value, 'buy')
                                percent = adj.get('buy_sell_percent', {}).get(find_key)
                                if percent:
                                    if value:
                                        value = value * ((100 + percent) / 100)  # TODO: calculate by adjustment

                        else:
                            list_value = current_asset[first_key]
                    except KeyError as e:
                        raise DoesNotExistsDataRecord(f"{first_key} -> {operand.split('.')[-1]} data is absent")
                if not is_calculate_field:
                    find_key = operand.split(".")[-1]
                    # buy_sell_percent_1[buy_plus_percent] || levels_crossed[buy] -> buy_plus_percent, buy, sell
                    value = filter_dicts_by_max_value(list_value, find_key)
    else:
        current_asset = asset
    return current_asset, value


def get_statements_result(statements, module_index, module=None, asset=None, adj=None):
    result_list = []
    statements_result = {}

    for index, statement in enumerate(sorted(statements, key=lambda x: x["sort_key"])):
        try:
            left_operand = statement.get("left_operand")
            right_operand = statement.get("right_operand")
            extra_settings = statement.get("extra_settings", {})

            current_asset, left_value = get_asset_or_value(
                extra_settings, asset, left_operand, side_operation="left", adj=adj
            )
            if left_value == N_A:
                return N_A
            if not left_value:
                left_value = get_operand_value(
                    left_operand, module_index, current_asset=current_asset, adj=adj
                )

            if isinstance(left_value, dict) and left_value.get("break"):
                index_rule_use = left_value.get("index_module_result")
                if module:
                    current_statement = module["rules"][index_rule_use]["statements"][
                        -1
                    ]  # find specific column
                    left_operand = current_statement.get("left_operand")
                    left_value = get_operand_value(
                        left_operand, module_index, current_asset=asset, adj=adj
                    )

            operator = statement["operator"]

            current_asset, right_value = get_asset_or_value(
                extra_settings, asset, right_operand, adj=adj
            )
            if right_value == N_A:
                return N_A

            if not right_value:
                right_value = get_operand_value(
                    right_operand, module_index, current_asset=current_asset, adj=adj
                )

            if left_value and right_value:
                then = statement["then"]
                try:
                    left_value_result = float(left_value)
                    right_value_result = float(right_value)
                    result_operators = operators
                except ValueError as e:
                    left_value_result = left_value
                    right_value_result = right_value
                    result_operators = str_operators

                if isinstance(right_value_result, list):
                    right_value_result, left_value_result = (
                        left_value_result,
                        right_value_result,
                    )
                try:

                    result = result_operators[operator](
                        left_value_result, right_value_result
                    )
                    statements_result[index] = {
                        "connector": statement.get("statement_connector", "or"),
                        "val": results[then] == result,
                    }
                    result_list.backendend(results[then] == result)
                except  KeyError as e:
                    return N_A

        except DoesNotExistsDataRecord as e:
            print(e, "EEREROOROROEOROEOROEORO!!!")
            raise ValueError(str(e))
    return get_answer(statements_result)


def get_module_result(module, module_index, asset, adj):
    sorted_rules = sorted(module["rules"], key=lambda x: x["sort_key_rule"])
    results_rules = {}
    for index, rule in enumerate(sorted_rules):
        result = get_statements_result(
            rule["statements"], module_index, module=module, asset=asset, adj=dict(adj)
        )
        if result == N_A:
            return N_A
        if rule.get("returned"):
            if result:
                return rule.get("returned_value")
        else:
            results_rules[index] = {
                "val": result,
                "connector": rule["rules_connector"],
                "returned": rule.get("returned"),
            }
    return get_answer(results_rules)

def get_last_m_asset(type_asset, current_date):
    # Get the last asset of the monthly
    filter_fields = {"period": "m", "type_asset": type_asset}

    start_of_current_month = datetime(current_date.year, current_date.month, 1)
    _, max_month_days = calendar.monthrange(current_date.year, current_date.month)
    end_of_current_month = datetime(
        current_date.year, current_date.month, max_month_days
    )
    filter_fields.update(
        {"date": {"$gte": start_of_current_month , "$lte": end_of_current_month}}
    )

    list_last_m_asset = list(
        Data.find(filter_fields)
        .sort([("date", pymongo.DESCENDING)])
        .limit(1)
    )
    last_m_asset = {}
    if list_last_m_asset:
        last_m_asset = list_last_m_asset[0]
    # except IndexError as e:
    #     last_m_asset = f"There are no data for {start_of_current_month.strftime('%B')} {current_date.year}"
    return last_m_asset

def check_empty_list(parent_field: str, list_of_values: list | dict, field_names: list) -> list:
    empty_fields = []
    if isinstance(list_of_values, dict):
        list_of_values = [list_of_values]
    for value, field in product(list_of_values, field_names):
        match value.get(field):
            case "":
                empty_fields.backendend(f"{parent_field}.{field}")
            case None:
                empty_fields.backendend(f"{parent_field}.{field}")
    return empty_fields

def check_data_asset(asset: dict) -> dict:
    empty_asset = []
    empty_last_asset = []
    last_m_asset = get_last_m_asset(asset["type_asset"], asset.get('date'))

    for field in CHECK_ASSETS_FIELDS:
        if field in ("buy_sell", "trend_values"):
            check_field = asset.get(field, [])
            children_fields = ("0", "3")
            if field == "buy_sell":
                children_fields = ("sell", "buy")
            empty_asset += check_empty_list(field, check_field, children_fields)
            continue

        match  asset.get(field):
            case None | "" | [] | {}:
                empty_asset.backendend(field)

    if not last_m_asset.get("momentum"):
        empty_last_asset.backendend(field)
    return {"current_asset": empty_asset, 'last_monthly': empty_last_asset}


def caluclate_modules_result(modules, asset, adjustments):
    global MODULE_RESULTS
    MODULE_RESULTS = {}
    original_modules = copy.deepcopy(modules)
    returned_result = {}
    for adj in adjustments:
        MODULE_RESULTS[str(adj['_id'])] = {}
        for index, module in enumerate(sorted(modules, key=lambda m: m.get("sort_key"))):
            # if MODULE_RESULTS[str(adj['_id'])].get(4):  # if module E is executed , so next modules should be N/A
            #     MODULE_RESULTS[str(adj['_id'])].update({index: N_A})
            #     continue
            result = get_module_result(module, index, asset=asset, adj=adj)

            if module.get("required_result_for_next_module"):
                MODULE_RESULTS[str(adj['_id'])].update({
                    index: result if result is not None else N_A
                })
            else:
                MODULE_RESULTS[str(adj['_id'])].update({index: result})
        for adj_id, module_info in MODULE_RESULTS.items():
            returned_result[adj_id] = {}

            for index_module, result_module in module_info.items():
                try:
                    if isinstance(result_module, int) and not isinstance(result_module, bool):
                        returned_result[adj_id].update({
                            modules[index_module]["name"]: (result_module is not None)
                        })
                    else:
                        returned_result[adj_id].update({
                            modules[index_module]["name"]: result_module or N_A
                        })
                except IndexError as e:
                    print(original_modules[index_module - 1]["name"], "skipped")
                    print("e", e)
    final_result = {}
    requires_modules = [f"Module {name}" for name in ["A", 'B', 'C']]
    for adj_id in returned_result:
        final_result[adj_id] = {}
        result_modules = returned_result[adj_id]
        for module_name, module_result in result_modules.items():
            if module_name in requires_modules:
                if module_result == N_A:
                    final_result[adj_id][module_name] = module_result
                    break
                else:
                    final_result[adj_id][module_name] = module_result
            else:
                final_result[adj_id][module_name] = module_result

    return final_result


def find_dict_index(list_of_dicts, key, value):
    """Returns the index of the first dictionary in list_of_dicts
    that has a value matching the given value for the given key"""
    for i, d in enumerate(list_of_dicts):
        if key in d and d[key] == value:
            return i
    return -1

def change_order_result_modules(modules_results, module_name):
    modules_results.update({module_name: modules_results.pop(module_name)})

def prepare_modules_results(results: dict) -> dict:
    modules_name = (
        "Module F", "Module G", "Module H", "Module I", "Module J", "Module K",
        "Module L", "Module M", "Module N", "Module O"
    )
    for modules_results, module in product(results.values(), modules_name):
        change_order_result_modules(modules_results, "Module F")
        if modules_results.get("Module E", '') != N_A:
            if module != 'Module F':
                modules_results[module] = N_A

    return results


import copy

if __name__ == "__main__":
    from modules_mock_data import modules as mock_modules


    def main():
        global MODULE_RESULTS
        MODULE_RESULTS = {}
        modules = sorted(mock_modules, key=lambda m: m.get("sort_key"))
        # modules = sorted([moduleD], key=lambda m: m.get('sort_key'))
        original_modules = copy.deepcopy(modules)
        for index, module in enumerate(modules):
            result = get_module_result(module, index, asset=ASSET)
            if module.get("required_result_for_next_module"):
                MODULE_RESULTS[index] = result if result is not None else N_A
            else:
                MODULE_RESULTS[index] = result

                # TODO: should be skipped if module has attr "skip"
            # if module.get('skip'):
            #     print(module['name'], 'skip!')
            #     index_from = module.get('continue_to')
            #     # index_from  = find_dict_index(modules , 'continue_to' , continue_to)
            #     modules = modules[:index_from - 1] + modules[index_from:]
            # print('index_from ' , index_from)
            print("= " * 10)
        returned_result = {}
        print(MODULE_RESULTS)
        for index_module, result_module in MODULE_RESULTS.items():
            try:
                if isinstance(result_module, int) and isinstance(result_module, bool):
                    returned_result[modules[index_module]["name"]] = (
                            result_module is not None
                    )
                else:
                    returned_result[modules[index_module]["name"]] = result_module
                # returned_result[modules[index_module]['name']] = result_module is not None if isinstance(result_module,
                #                                                                                          int) and result_module not in [
                #                                                                                   True,
                #                                                                                   False] else result_module
                # print(modules[index_module]['name'],
                #       result_module is not None if isinstance(result_module, int)
                #                                    and result_module not in [True, False] else result_module , "SSDLSKDKLSKDLSDLKSLDKKDSL")
                # # result_module)
            except IndexError as e:
                print(original_modules[index_module - 1]["name"], "skipped")
                print("e", e)


    main()
