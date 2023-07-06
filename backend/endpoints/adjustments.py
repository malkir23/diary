import datetime

import pymongo
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from starlette.responses import JSONResponse

from backend.models.adjustments import AdjustmentModel, AdjustmentUpdateModel, AdjustmentModelMixin
from backend.services.logs import LogsService, TYPES_LOGS
from backend.services.mongo import MongoService
from backend.services.oauth2 import check_admin, check_auth
from backend.settings.config import settings
from backend.db.base import Adjustment

router = APIRouter()
AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
AVAILABLE_PERIOD = settings.AVAILABLE_PERIOD

ADJUSTMENT_DATES_FIELDS = ['created_at', 'updated_at']
ADJUSTMENT_UPDATES_FIELDS = ['assets']
ADJUSTMENT_TYPE_LOG = TYPES_LOGS.ADJUSTMENT


@router.get('/get_all_available_assets')
def get_all_available_assets():
    return [db_name for db_name , name_api in settings.AVAILABLE_ASSETS]


@router.post('/adjustment')
def create_config_table(item: AdjustmentModel, background_tasks: BackgroundTasks,
                        auth_user: dict = Depends(check_admin),
                        user: dict = Depends(check_auth), ) -> JSONResponse:
    user_id = user['id']
    payload = item.dict()
    now = datetime.datetime.now()
    for date_field in ADJUSTMENT_DATES_FIELDS:
        payload[date_field] = now
    last_adjustment = Adjustment.find({}).sort([("created_at", pymongo.DESCENDING)]).limit(1)[0]
    sort_key = last_adjustment.get('sort_key') + 1
    payload['sort_key'] = sort_key
    result = Adjustment.insert_one(payload)
    if result:
        try:
            background_tasks.add_task(LogsService, before_object={}, after_object=payload, type_=ADJUSTMENT_TYPE_LOG,
                                      action='create', fields=["name", "buy_sell_percent.buy_plus",
                                                               'buy_sell_percent.sell_minus', 'trend_values.1',
                                                               'trend_values.2', 'assets'], user_id=user_id,
                                      obj=payload)
        except Exception as e:
            print(f'Error create log for adjustment [CREATE] {str(e)}')
        return JSONResponse(MongoService.normalize_mongo_obj(payload, dates_fields=ADJUSTMENT_DATES_FIELDS))
    else:
        return JSONResponse({
            'msg': 'Error write to db. Please contact with administrator.'
        })


@router.put('/adjustment/{adjustment_id}', status_code=status.HTTP_200_OK)
def update_adjustment(adjustment_id: str, item: AdjustmentUpdateModel,
                      background_tasks: BackgroundTasks,
                      auth_user: dict = Depends(check_admin),
                      user: dict = Depends(check_auth)
                      ) -> JSONResponse:
    MongoService.is_valid_mongo_id(adjustment_id)
    current_adj = Adjustment.find_one({"_id": ObjectId(adjustment_id)})
    if not current_adj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Adjustment not found')
    user_id = user['id']
    payload = item.dict()
    name = payload.get('name', '').strip()
    if name:
        adj = list(Adjustment.find({"_id": {"$ne": ObjectId(adjustment_id)}, "name": name}))
        if adj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Adjustment already exists with name "{name}"')
    payload_for_update = MongoService.convert_2_dict_mongodb(payload, remove_nulls=True, now_updated=True)
    result = Adjustment.update_one({'_id': ObjectId(adjustment_id)}, {'$set': payload_for_update})

    if result.modified_count:
        try:
            background_tasks.add_task(LogsService, before_object=MongoService.convert_2_dict_mongodb(current_adj),
                                      after_object=payload_for_update, type_=ADJUSTMENT_TYPE_LOG,
                                      action='update', fields=["name", 'assets',
                                                               'buy_sell_percent.buy_plus',
                                                               'buy_sell_percent.sell_minus',
                                                               'trend_values.1', 'trend_values.2'], user_id=user_id,
                                      obj={"id": adjustment_id, **payload})
        except Exception as e:
            print(f'Error create log for adjustment [UPDATE] {str(e)}')
        return JSONResponse(MongoService.normalize_mongo_obj(Adjustment.find_one({'_id': ObjectId(adjustment_id)}),
                                                             dates_fields=ADJUSTMENT_DATES_FIELDS))
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong')


@router.delete('/adjustment/{adjustment_id}')
def delete_adjustment(adjustment_id,
                      background_tasks: BackgroundTasks,
                      auth_user: dict = Depends(check_admin),
                      user: dict = Depends(check_auth)
                      ):
    MongoService.is_valid_mongo_id(adjustment_id)
    current_adj = dict(Adjustment.find_one({"_id": ObjectId(adjustment_id)}))
    if not current_adj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjustment not found.")
    if current_adj.get('is_default'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='The default adjustment cannot  be deleted.')
    user_id = user['id']
    result = Adjustment.delete_one({'_id': ObjectId(adjustment_id)})
    if not result.deleted_count:
        raise HTTPException(status_code=500, detail='Adjustment is not deleted  successfully')
    try:
        background_tasks.add_task(LogsService, before_object={}, after_object={}, type_=ADJUSTMENT_TYPE_LOG,
                                  action='delete', user_id=user_id, fields=None,
                                  obj=MongoService.normalize_mongo_obj(current_adj))
    except Exception as e:
        print(f'Error create log for adjustment [DELETE] {str(e)}')
    return {'result': True}


@router.get('/adjustment/{adjustment_id}')
def get_adjustment(adjustment_id):
    MongoService.is_valid_mongo_id(adjustment_id)
    adjustment = Adjustment.find_one({'_id': ObjectId(adjustment_id)})
    if adjustment:
        return MongoService.normalize_mongo_obj(adjustment, dates_fields=ADJUSTMENT_DATES_FIELDS)
    else:
        raise HTTPException(status_code=400, detail=f'Adjustment does not exists with id {adjustment_id}')


@router.get('/list')
def get_all_adjustments():
    result = Adjustment.find({}).sort([("sort_key" , 1)])
    return MongoService.data_list_to_json(result)
