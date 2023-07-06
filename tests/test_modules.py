from backend.services.modules import caluclate_modules_result
from backend.services.modules_mock_data import modules
from backend.db.base import Data, Adjustment
from backend.settings.config import settings
from tests.data_test import expected_result, template_adjustment


def test_settings_mode():
    assert settings.TESTING is True

def test_insert_adjustment():
    assert Adjustment.insert_one(template_adjustment)

def test_insert_assets(template_month_asset):
    assert Data.insert_many(template_month_asset)


def check_result(actual_result_key, actual_result_value):
    assert actual_result_value == expected_result.get(actual_result_key)

def test_module():
    monthly_asset = Data.find_one({"period": "m"})
    result = caluclate_modules_result(list(modules), asset=monthly_asset)
    [check_result(key, value) for key, value in result.items()]
