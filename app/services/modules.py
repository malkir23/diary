# import pymongo
from bson import ObjectId
from app.services.modules_mock_data import TOP, BOTTOM, MID, BULLISH, BEARISH

if __name__ != "__main__":
    from fastapi import HTTPException, status
    import pymongo
    from app.db.base import Data

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


class DoesNotExistsDataRecord(Exception):
    pass


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def filter_dicts_by_max_value(dicts, key) -> int | float | None:
    result = []
    if not dicts:
        return
    values = [d[key] for d in dicts if d.get(key)] + [0, 0]
    return max(*values)
    # if dicts:
    #     max_value = max()
    #     result = [d for d in dicts if d[key] == max_value]
    # return result


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
            # raise DoesNotExistsDataRecord(
            #     f'value in {operand} is absent for record with id {current_asset.get("_id")}'
            # )
    elif isinstance(operand, str) and "module_index_" in operand:
        index_module_result = int(operand.replace("module_index_", ""))
        if index_module_result in MODULE_RESULTS[str(adj['_id'])]:
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
        if order and order == 'last' and type_ == 'max':
            filter_fields = {"period": period, "type_asset": type_asset}
            current_asset = (
                Data.find(filter_fields)
                .sort([("date", pymongo.DESCENDING)])
                .limit(1)[0]
            )
            first_key = operand.split(".")[0]
            find_key = operand.split(".")[-1]

            list_value = current_asset[first_key]
            value = filter_dicts_by_max_value(list_value, find_key)
        else:

            if order and order == "last":

                filter_fields = {"period": period, "type_asset": type_asset}
                if __name__ == "__main__":
                    current_asset = LAST_MONTHLY_ASSET
                else:
                    current_asset = (
                        Data.find(filter_fields)
                        .sort([("date", pymongo.DESCENDING)])
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
                            # print(current_asset)
                            list_value = current_asset[first_key]
                    except KeyError as e:
                        raise DoesNotExistsDataRecord(f"{first_key} -> {operand.split('.')[-1]} data is absent")
                if not is_calculate_field:
                    find_key = operand.split(".")[
                        -1]  # buy_sell_percent_1[buy_plus_percent] || levels_crossed[buy] -> buy_plus_percent, buy, sell
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

                result = result_operators[operator](
                    left_value_result, right_value_result
                )
                statements_result[index] = {
                    "connector": statement.get("statement_connector", "or"),
                    "val": results[then] == result,
                }
                result_list.append(results[then] == result)
        except DoesNotExistsDataRecord as e:
            print(e, "EEREROOROROEOROEOROEORO!!!")
            right_value = None
            left_value = None
            raise ValueError(str(e))
    return get_answer(statements_result)


def get_module_result(module, module_index, asset, adj):
    sorted_rules = sorted(module["rules"], key=lambda x: x["sort_key_rule"])
    results_rules = {}
    for index, rule in enumerate(sorted_rules):
        result = get_statements_result(
            rule["statements"], module_index, module=module, asset=asset, adj=dict(adj)
        )

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


def caluclate_modules_result(modules, asset, adjustments):
    global MODULE_RESULTS
    MODULE_RESULTS = {}
    original_modules = copy.deepcopy(modules)
    returned_result = {}
    for adj in adjustments:
        MODULE_RESULTS[str(adj['_id'])] = {}
        for index, module in enumerate(sorted(modules, key=lambda m: m.get("sort_key"))):
            result = get_module_result(module, index, asset=asset, adj=adj)
            # print(module["name"], result)
            if module.get("required_result_for_next_module"):
                MODULE_RESULTS[str(adj['_id'])].update({
                    index: result if result is not None else N_A
                })
            else:
                MODULE_RESULTS[str(adj['_id'])].update({index: result})
            # print("= " * 10)
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

    return returned_result


def find_dict_index(list_of_dicts, key, value):
    """Returns the index of the first dictionary in list_of_dicts
    that has a value matching the given value for the given key"""
    for i, d in enumerate(list_of_dicts):
        if key in d and d[key] == value:
            return i
    return -1


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
            print(module["name"], result)
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
