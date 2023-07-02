from functools import reduce


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


from app.settings.config import settings
from fastapi import HTTPException, status

AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD


def check_period_asset_valid(period, type_asset):
    if period not in AVAILABLE_PERIOD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'period must be "{", ".join(AVAILABLE_PERIOD)}"',
        )
    if type_asset not in AVAILABLE_ASSETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"type_asset must be one of {AVAILABLE_ASSETS}",
        )
