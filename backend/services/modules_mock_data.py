BULLISH = 'BULLISH'
BEARISH = 'BEARISH'

SELL_X = 'sell x'
SELL_2X = 'sell 2x'
BUY_X = 'buy x'
BUY_2X = 'buy 2x'
BOTTOM = 'bottom'
MID = 'mid'
TOP = 'top'
N_A = "N/A"
SELL_ENTIRE_POSITION = "Sell Entire Position"

moduleA = {
    "name": "Module A",
    "sort_key": 0,
    "required_result_for_next_module": True,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": 0,  # index rules in module
            "statements": [
                {
                    "left_operand": "trend_length",
                    "operator": ">=",
                    "right_operand": 20,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                }
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": 1,  # index rules in module
            "statements": [
                {
                    "left_operand": "trend_length",
                    "operator": ">=",
                    "right_operand": 10,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                }
            ],
        },
        {
            "sort_key_rule": 2,
            "rules_connector": "or",
            "returned": True,
            "returned_value": 2,  # index rules in module
            "statements": [
                {
                    "left_operand": "trend_length",
                    "operator": ">=",
                    "right_operand": 6,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleB = {
    "name": "Module B",
    "sort_key": 1,
    "required_result_for_next_module": True,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            # 'returned': True,
            # 'returned_value': 0, # index rules in module
            "statements": [
                {
                    "left_operand": "prev_module_rule_index_0",
                    "operator": "==",
                    "right_operand": None,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "trend_percent",
                    "operator": ">=",
                    "right_operand": 10,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            # 'returned': True,
            # 'returned_value': 1,  # index rules in module
            "statements": [
                {
                    "left_operand": "prev_module_rule_index_1",
                    "operator": "==",
                    "right_operand": None,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "trend_percent",
                    "operator": ">=",
                    "right_operand": 20,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                },
            ],
        },
        {
            "sort_key_rule": 2,
            "rules_connector": "or",
            # 'returned': True,
            # 'returned_value': 2,  # index rules in module
            "statements": [
                {
                    "left_operand": "prev_module_rule_index_2",
                    "operator": "==",
                    "right_operand": None,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "trend_percent",
                    "operator": ">=",
                    "right_operand": 30,
                    "then": "yes",
                    "statement_connector": "or",
                    "sort_key": 0,
                },
            ],
        },
    ],
}

moduleC = {
    "name": "Module C",
    "sort_key": 2,
    "required_result_for_next_module": False,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "statements": [
                {
                    "left_operand": "close",
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "period": "m",
                        "order": "last",
                        "operand": "right",
                        "type": 'max'
                    },
                    "right_operand": "levels_crossed.buy",  # column K
                    "then": "yes",
                    "sort_key": 0,
                },
            ],
        },
    ],
}

moduleD = {
    "name": "Module D",
    "sort_key": 3,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BOTTOM,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": ">",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.1",
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 0,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": MID,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": ">",
                    "right_operand": "trend_values.1",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.2",
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 0,
                },
            ],
        },
        {
            "sort_key_rule": 2,
            "rules_connector": "or",
            "returned": True,
            "returned_value": TOP,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": ">",
                    "right_operand": "trend_values.2",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.3",
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 0,
                },
            ],
        },
    ],
}

moduleE = {
    "name": "Module E",
    "sort_key": 4,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": BOTTOM,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BULLISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_2X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": MID,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BULLISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 2,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": TOP,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BULLISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 3,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": BOTTOM,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BEARISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 4,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": MID,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BEARISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 5,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": TOP,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BEARISH,
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 1,
                },
            ],
        },
    ],
}

moduleF = {
    "name": "Module F",
    "sort_key": 5,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": SELL_X,
            "statements": [
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "==",
                    "right_operand": MID,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "extra_settings": {  # last monthly by current assets
                        "period": "m",
                        "order": "last",
                        "operand": "left",
                    },
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BULLISH,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BEARISH,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 2,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": N_A,
            "statements": [
                {
                    "extra_settings": {  # last monthly by current assets
                        "period": "m",
                        "order": "last",
                        "operand": "left",
                    },
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BULLISH,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "momentum",
                    "operator": "==",
                    "right_operand": BEARISH,
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
                {
                    "left_operand": "module_index_3",  # index moduleD
                    "operator": "in",
                    "right_operand": [TOP, BOTTOM],
                    "then": "yes",
                    # "statement_connector": "and",
                    "sort_key": 2,
                },
            ],
        },
    ],
}

moduleG = {
    "name": "Module G",
    "sort_key": 6,
    "skip": True,
    "continue_to": 8,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "extra_settings": {
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "buy_sell_percent.sell_minus",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": None,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "buy_sell_percent.sell_minus",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": ">",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
    ],
}

moduleH = {
    "name": "Module H",
    "sort_key": 7,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_2X,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "levels_crossed.sell",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": ">",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": None,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": "<",
                    "right_operand": "levels_crossed.sell",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
    ],
}

moduleI = {
    "name": "Module I",
    "sort_key": 8,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": ">",
                    "right_operand": "trend_values.3",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "buy_sell_percent.buy_plus",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": None,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": "<=",
                    "right_operand": "trend_values.3",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<=",
                    "extra_settings": {
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "buy_sell_percent.buy_plus",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 1,
                },
            ],
        },
    ],
}

moduleJ = {
    "name": "Module J",
    "sort_key": 9,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "levels_crossed.buy",
                    "then": "yes",
                    "sort_key": 0,
                }
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            "returned": True,
            "returned_value": None,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "levels_crossed.buy",
                    "then": "yes",
                    "statement_connector": "and",
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleK = {
    "name": "Module K",
    "sort_key": 10,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": BUY_X,
            "statements": [
                {
                    "left_operand": "close",  # index moduleD
                    "operator": ">",
                    "extra_settings": {  # last monthly by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "levels_crossed.buy",
                    "then": "yes",
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleL = {
    "name": "Module L",
    "sort_key": 11,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            "returned": True,
            "returned_value": SELL_ENTIRE_POSITION,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.2",
                    "then": "yes",
                    # 'statement_connector': 'or',
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleM = {
    "name": "Module M",
    "sort_key": 12,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "buy_sell_percent.sell_minus",
                    "extra_settings": {  # max monthly value  by current assets
                        "type": "max",
                        "operand": "right",
                    },
                    "then": "yes",
                    # 'statement_connector': 'or',
                    "sort_key": 0,
                }
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_indicator",
                    "then": "yes",
                    # 'statement_connector': 'or',
                    "sort_key": 0,
                }
            ],
        },
        {
            "sort_key_rule": 2,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    # 'statement_connector': 'or',
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleN = {
    "name": "Module N",
    "sort_key": 13,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "extra_settings": {
                        "type": "max",
                        "operand": "right",
                    },
                    "right_operand": "buy_sell_percent.sell_minus",
                    "then": "yes",
                    'statement_connector': 'and',
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_indicator",
                    "then": "yes",
                    'statement_connector': 'and',
                    "sort_key": 1,
                }
            ],
        },
        {
            "sort_key_rule": 1,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_X,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_values.0",
                    "then": "yes",
                    # 'statement_connector': 'or',
                    "sort_key": 0,
                }
            ],
        },
    ],
}

moduleO = {
    "name": "Module O",
    "sort_key": 14,
    "rules": [
        {
            "sort_key_rule": 0,
            "rules_connector": "or",
            'returned': True,
            'returned_value': SELL_ENTIRE_POSITION,
            "statements": [
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "buy_sell_percent.sell_minus",
                    "extra_settings": {
                        "type": "max",
                        "operand": "right",
                    },
                    "then": "yes",
                    # 'statement_connector': 'and',
                    "sort_key": 0,
                },
                {
                    "left_operand": "close",
                    "operator": "<",
                    "right_operand": "trend_indicator",
                    "then": "yes",
                    'statement_connector': 'or',
                    "sort_key": 1,
                }
            ],
        },
        # {
        #     "sort_key_rule": 1,
        #     "rules_connector": "or",
        #     # 'returned': True,
        #     # 'returned_value': 'Sell Entire Postion',
        #     "statements": [
        #         {
        #             "left_operand": "close",
        #             "operator": "<",
        #             "right_operand": "trend_indicator",
        #             "then": "yes",
        #             # 'statement_connector': 'or',
        #             "sort_key": 0,
        #         }
        #     ],
        # },
    ],
}

modules = [
    moduleA,
    moduleB,
    moduleC,
    moduleD,
    moduleE,
    moduleF,
    moduleG,
    moduleH,
    moduleI,
    moduleJ,
    moduleK,
    moduleL,
    moduleM,
    moduleN,
    moduleO,
]
