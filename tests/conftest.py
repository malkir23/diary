from copy import deepcopy

from backend.main import backend
from backend.settings.config import settings
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
#     backend.dependency_overrides[AuthJWT] = MagicMock()
#     return TestClient(backend)
# #     return TestClient(backend)
