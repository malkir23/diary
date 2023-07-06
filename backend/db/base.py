from backend.settings.config import settings
from pymongo import ASCENDING, mongo_client
from mongomock import MongoClient as MockMongoClient

class ConnectionDB:
    __instance = None

    class __ConnectionDB:
        def __init__(self):
            # Initialise mongo client
            if not settings.TESTING:
                self.client = mongo_client.MongoClient(settings.DATABASE_URL)
            else:
                self.client = MockMongoClient()

    def __init__(self):
        if not ConnectionDB.__instance:
            ConnectionDB.__instance = ConnectionDB.__ConnectionDB()

    def __getattr__(self, item):
        return getattr(self.__instance, item)


class FuzzyTables(ConnectionDB):
    @staticmethod
    def user(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE

        user = ConnectionDB().client[database_name].users
        user.create_index([("email", ASCENDING)], unique=True)
        return user

    @staticmethod
    def data(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        data = ConnectionDB().client[database_name].data
        return data

    @staticmethod
    def modules(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        modules = ConnectionDB().client[database_name].modules
        return modules

    @staticmethod
    def config(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        config = ConnectionDB().client[database_name].config
        return config

    @staticmethod
    def adjustment(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        config_table = ConnectionDB().client[database_name].adjustment
        return config_table

    @staticmethod
    def logs(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        logs = ConnectionDB().client[database_name].logs
        return logs

    @staticmethod
    def asset_extra_data(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        asset_extra_data = ConnectionDB().client[database_name].asset_extra_data
        return asset_extra_data


user_db = FuzzyTables.user()
Data = FuzzyTables.data()
Modules = FuzzyTables.modules()
Config = FuzzyTables.config()
Adjustment = FuzzyTables.adjustment()
Logs = FuzzyTables.logs()
AssetExtraData = FuzzyTables.asset_extra_data()
