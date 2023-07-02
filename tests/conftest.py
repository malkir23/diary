from copy import deepcopy

from app.main import app
from app.settings.config import settings
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pytest import fixture
from tests.data_test import template_asset, periods

settings.TESTING = True


def create_assets_diff(period):
    copy_asset = deepcopy(template_asset)
    copy_asset["period"] = period
    return copy_asset


@fixture
def template_month_asset():
    return [create_assets_diff(period) for period in periods]


# @pytest.fixture(scope="session")
# def client():
# https://github.com/tiangolo/fastapi/issues/5253
#     app.dependency_overrides[AuthJWT] = MagicMock()
#     return TestClient(app)
# #     return TestClient(app)
