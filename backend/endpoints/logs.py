import pymongo
from fastapi import APIRouter, HTTPException, status, Depends

from backend.db.base import Logs
from backend.services.logs import LogsService, TYPES_LOGS
from backend.services.mongo import MongoService
from backend.services.oauth2 import check_auth

router = APIRouter()


@router.get('/get')
async def get(
        type_log=None,
        action=None,
        page: int = 1,
        count: int = 30,
        date_from=None,
        date_to=None,
        type_asset=None,
        period=None,
        attribute=None,
        user_id=None,
        auth_user: dict = Depends(check_auth)
):
    if type_log and type_log not in LogsService.TYPES_LOGS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{type_log} is not valid. Should be {" ".join(LogsService.TYPES_LOGS)}')
    if action and action not in LogsService.ACTIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'{action} is not valid. Should be {" ".join(LogsService.ACTIONS)}')
    date_from_db, date_to_db = None, None
    if date_from:
        date_from_db = MongoService.string_to_date_mongo(date_from)
    if date_to:
        date_to += " 23:59:59"
        date_to_db = MongoService.string_to_date_mongo(date_to, "%Y-%m-%d %H:%M:%S")
    filter_fields = {}
    if type_log:
        filter_fields['type_'] = type_log
    if action:
        filter_fields['action'] = action
    if user_id:
        filter_fields['user_id'] = user_id

    if date_from_db and date_to_db:
        filter_fields["create_at"] = {"$gte": date_from_db, "$lte": date_to_db}
    match type_log:
        case TYPES_LOGS.ASSET:
            try:
                filters_asset = LogsService.get_asset_filter_logs(type_asset, period, attribute)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            else:
                filter_fields.update(filters_asset)

    if page <= 0 or count <= 0:
        message = "count or page can be less than 0"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    skip_count = (page - 1) * count
    logs = Logs.aggregate([
        {"$match": filter_fields},
        {"$sort": {"create_at": pymongo.DESCENDING}},
        {
            "$lookup":{
                "let": { "userObjId": { "$toObjectId": "$user_id" } },
                "from": 'users',
                "pipeline":[
                    { "$match": { "$expr": { "$eq": [ "$_id", "$$userObjId" ] } } },
                    {"$project": {  "_id": 0, "name": 1 } }
                ],
                "as": "user"
            }
        },
        {"$skip": skip_count},
        {"$limit": count },
        {
            "$addFields": { "user": { "$arrayElemAt": [ "$user", 0 ] } }
        }
    ])
    return {
        'logs': MongoService.data_list_to_json(logs),
        "count": Logs.count_documents(filter_fields)
    }
