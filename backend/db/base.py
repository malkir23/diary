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
    def logs(database_name=None):
        if not database_name:
            database_name = settings.MONGO_INITDB_DATABASE
        logs = ConnectionDB().client[database_name].logs
        return logs


user_db = FuzzyTables.user()
Logs = FuzzyTables.logs()
