from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from backend.services.utils import remove_nulls_from_dict


class MongoService:
    @staticmethod
    def data_to_json(obj):
        if not obj: return {}
        obj["id"] = str(obj["_id"])
        del obj["_id"]
        return obj

    @staticmethod
    def data_list_to_json(list_of_data):
        return [MongoService.data_to_json(d) for d in list_of_data]

    @staticmethod
    def mapped_keys_mongo(fields):
        return {f: f"${f}" for f in fields}

    @staticmethod
    def convert_2_dict_mongodb(obj, deleted_keys=[], remove_nulls=False, now_updated=False, now_created=False):
        result = {}
        for key, val in obj.items():
            if not isinstance(val, dict):
                result[key] = val
                continue

            for sub_key, sub_val in val.items():
                new_key = "{}.{}".format(key, sub_key)
                result[new_key] = sub_val
                if not isinstance(sub_val, dict):
                    continue
                result.update(MongoService.convert_2_dict_mongodb(result))
                if new_key in result:
                    del result[new_key]
        # remove keys
        if deleted_keys:
            for del_key in deleted_keys:
                if del_key in result:
                    del result[del_key]
        if remove_nulls:
            result = remove_nulls_from_dict(result)
        if now_created:
            result['created_at'] = datetime.now()
        if now_updated:
            result['updated_at'] = datetime.now()
        return result

    @staticmethod
    def is_valid_mongo_id(mongo_id, error_msg=None):
        try:
            ObjectId(mongo_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=(error_msg or 'Id is invalid') + f': {mongo_id}')

    @staticmethod
    def normalize_mongo_obj(obj, dates_fields=None):
        obj['id'] = str(obj['_id'])
        del obj['_id']
        if dates_fields:
            for date_field in dates_fields:
                obj[date_field] = str(obj[date_field])
        return obj

    @staticmethod
    def string_to_date_mongo(str_value, format_date="%Y-%m-%d"):
        try:
            return datetime.strptime(str_value, format_date)
        except Exception:
            return None

    @staticmethod
    def convert_to_mongo_ids(ids):
        return list(map(lambda _id: ObjectId(_id), ids))
